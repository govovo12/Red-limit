import asyncio
from collections import defaultdict

# === 錯誤碼與工具 ===
from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.env.config_loader import get_ws_base_url_by_game_type, R88_GAME_WS_ORIGIN
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.ws.ws_connection_async_helper import (
    open_ws_connection,
    close_ws_connection,
    start_ws_async,
)
from workspace.tools.ws.ws_event_dispatcher_async import register_event_handler, clear_handlers
from workspace.tools.ws.ws_step_runner_async import run_ws_step_async
from workspace.tools.ws.report_helper import report_step_result

# === 任務模組 ===
from workspace.modules.task.unlock_wallet_task import unlock_wallet
from workspace.modules.task.check_account_task import check_account_exists
from workspace.modules.task.recharge_wallet_task import recharge_wallet_async
from workspace.modules.type2_ws.open_ws_connection_task import open_ws_connection_task
from workspace.modules.type2_ws.handle_join_room_async import handle_join_room_async
from workspace.modules.type2_ws.send_heartbeat_task import send_heartbeat_async, handle_heartbeat_response
from workspace.modules.type2_ws.send_bet_task import send_bet_async
from workspace.modules.type2_ws.parse.parse_bet_response import handle_bet_ack
from workspace.modules.type2_ws.send_round_finished import send_round_finished_async, handle_round_finished_ack
from workspace.modules.type2_ws.send_exit_room import send_exit_room_async, handle_exit_room_ack


class TaskContext:
    def __init__(self, task):
        self.task = task
        self.account = task.get("account")
        self.oid = task.get("oid")
        self.token = task.get("access_token")
        self.game_name = task.get("game_name")
        self.game_type = task.get("game_option_list_type")
        self.ws = None
        self.ok = True
        self.code = None
        self.pf_account = None

# Step 0: 驗證參數
async def step_0_prepare(ctx: TaskContext):
    print_info(f"[Step 0] 接收主控參數 account={ctx.account}, oid={ctx.oid}, game={ctx.game_name}")
    if not ctx.account or not ctx.oid or not ctx.token:
        ctx.ok = False
        ctx.code = ResultCode.INVALID_TASK
        log_step_result(ctx.code, step="prepare", account=ctx.account, game_name=ctx.game_name)

# Step 0.5: 查詢 pf_account 對應關係
async def step_0_5_check_account(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info("[Step 0.5] 查詢 pf_account 對應關係中...")

    code, pf_account = await check_account_exists(ctx.account)
    report_step_result(ctx, code, step="check_account", error_records=error_records)

    if ctx.ok:
        ctx.pf_account = pf_account
        print_info(f"[Step 0.5] ✅ pf_account 對應成功：{pf_account}")

# Step 0.6: 解鎖錢包（使用統一錯誤控制架構）
async def step_0_6_unlock_wallet(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info("[Step 0.6] 嘗試解鎖錢包...")

    code = await unlock_wallet(ctx.pf_account)
    report_step_result(ctx, code, step="unlock_wallet", error_records=error_records)

    if ctx.ok:
        print_info("[Step 0.6] ✅ 錢包已成功解鎖")


# Step 1: 錢包加值（已改為使用 report_step_result 控制）
async def step_1_recharge_wallet(ctx: TaskContext, error_records):
    if not ctx.ok:
        return

    print_info("[Step 1] 錢包加值中...")

    code = await recharge_wallet_async(ctx.account)
    report_step_result(ctx, code, step="recharge_wallet", error_records=error_records)

    if ctx.ok:
        print_info("[Step 1] ✅ 加值成功")


# Step 2: 建立 WS 並啟動接收
async def step_2_open_ws(ctx: TaskContext, error_records):
    if not ctx.ok:
        return

    print_info("[Step 2] 建立 WebSocket 連線中...")

    ws_url = f"{get_ws_base_url_by_game_type(ctx.game_type)}?token={ctx.token}&oid={ctx.oid}"
    code, ws = await open_ws_connection_task(ws_url, R88_GAME_WS_ORIGIN)

    report_step_result(ctx, code, step="open_ws", error_records=error_records)

    if not ctx.ok:
        return

    # 成功才補上 context 設定
    ctx.ws = ws
    ctx.ws._join_event = asyncio.Event()
    ctx.ws.account = ctx.account
    ctx.ws.game_name = ctx.game_name

    register_event_handler(ctx.ws, "join_room", handle_join_room_async)
    register_event_handler(ctx.ws, "keep_alive", handle_heartbeat_response)
    register_event_handler(ctx.ws, "bet", handle_bet_ack)
    register_event_handler(ctx.ws, "cur_round_finished", handle_round_finished_ack)
    register_event_handler(ctx.ws, "exit_room", handle_exit_room_ack)

    asyncio.create_task(start_ws_async(ctx.ws))


# Step 3: 等待 join_room
async def step_3_wait_join_room(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return

    print_info("[Step 3] 等待 join_room 封包")
    try:
        await asyncio.wait_for(ctx.ws._join_event.wait(), timeout=10)
    except asyncio.TimeoutError:
        report_step_result(ctx, ResultCode.TASK_WS_TIMEOUT, step="join_room_timeout", error_records=error_records)
        return

    code = ctx.ws.error_code
    report_step_result(ctx, code, step="join_room", error_records=error_records)




# Step 4: 發送 keep_alive
async def step_4_keep_alive(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 4] 發送 keep_alive 封包")
    code = await run_ws_step_async(
        ws_obj=ctx.ws,
        event_name="keep_alive",
        request_data={"event": "keep_alive"},
    )
    report_step_result(ctx, code, step="keep_alive", error_records=error_records)


# Step 5: 發送 bet 封包
async def step_5_send_bet(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 5] 發送 bet 封包")
    code = await send_bet_async(ctx.ws)
    ctx.ws.callback_done = asyncio.Event()
    report_step_result(ctx, code, step="send_bet", error_records=error_records)


# Step 6: 等待 bet_ack 封包
async def step_6_bet_ack(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 6] 等待 bet_ack 封包")
    code = await run_ws_step_async(
        ws_obj=ctx.ws,
        event_name="bet",
        request_data={},
    )
    report_step_result(ctx, code, step="bet_ack", error_records=error_records)


# Step 7: 發送 cur_round_finished 封包
async def step_7_round_finish(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 7] 發送 cur_round_finished 封包")
    code = await run_ws_step_async(
        ws_obj=ctx.ws,
        event_name="cur_round_finished",
        request_data={"event": "cur_round_finished"},
    )
    report_step_result(ctx, code, step="cur_round_finished", error_records=error_records)


# Step 8: 發送 exit_room 封包
async def step_8_exit_room(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 8] 發送 exit_room 封包")
    code = await run_ws_step_async(
        ws_obj=ctx.ws,
        event_name="exit_room",
        request_data={"event": "exit_room"},
    )
    report_step_result(ctx, code, step="exit_room", error_records=error_records)
    clear_handlers(ctx.ws)






# === 主流程 ===
def ws_connection_flow(task_list, max_concurrency: int = 1):
    async def async_flow():


        error_records = []
        step_success_records = []
        contexts = [TaskContext(t) for t in task_list]

        await asyncio.gather(*[step_0_prepare(ctx) for ctx in contexts])
        await asyncio.gather(*[step_0_5_check_account(ctx) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_0_6_unlock_wallet(ctx) for ctx in contexts if ctx.ok]) 
        await asyncio.gather(*[step_1_recharge_wallet(ctx, step_success_records, error_records) for ctx in contexts if ctx.ok])  
        await asyncio.gather(*[step_2_open_ws(ctx) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_3_wait_join_room(ctx) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_4_keep_alive(ctx, step_success_records, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_5_send_bet(ctx, step_success_records, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_6_bet_ack(ctx, step_success_records, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_7_round_finish(ctx, step_success_records, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_8_exit_room(ctx, step_success_records, error_records) for ctx in contexts if ctx.ok])

        success = sum(1 for ctx in contexts if ctx.ok)
        print_info(f"[Flow ✅] 全部完成，共成功 {success} 筆，失敗 {len(error_records)} 筆")

        if error_records:
            print_error("❌ 子控失敗清單如下：")
            for err in error_records:
                label = "⚠ WARNING" if err["code"] == ResultCode.TASK_BET_MISMATCHED else "❌ ERROR"
                print_error(f"{label} code={err['code']} | step={err['step']} | account={err.get('account')} | game={err.get('game_name')}")

            failed_accounts = {err['account'] for err in error_records if 'account' in err}
            filtered_steps = [rec for rec in step_success_records if rec["account"] in failed_accounts]

            if filtered_steps:
                print_info("\n📊 失敗任務中各步驟成功統計：")
                grouped = defaultdict(list)
                for rec in filtered_steps:
                    key = (rec["account"], rec["game_name"])
                    grouped[key].append(rec["step"])

                for (account, game_name), steps in grouped.items():
                    print_info(f"\n🔸 account={account} | game={game_name}")
                    for step in steps:
                        print_info(f"  ✅ {step}")

        return [ctx.code for ctx in contexts if not ctx.ok]

    return asyncio.run(async_flow())