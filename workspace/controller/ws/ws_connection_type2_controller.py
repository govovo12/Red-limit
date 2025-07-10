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
from workspace.tools.ws.ws_event_dispatcher_async import register_event_handler,clear_handlers
from workspace.tools.ws.ws_step_runner_async import run_ws_step_async

# === 任務模組 ===
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


# Step 0: 驗證參數
async def step_0_prepare(ctx: TaskContext):
    print_info(f"[Step 0] 接收主控參數 account={ctx.account}, oid={ctx.oid}, game={ctx.game_name}")
    if not ctx.account or not ctx.oid or not ctx.token:
        ctx.ok = False
        ctx.code = ResultCode.INVALID_TASK
        log_step_result(ctx.code, step="prepare", account=ctx.account, game_name=ctx.game_name)


# Step 1: 錢包加值
async def step_1_recharge_wallet(ctx: TaskContext, step_success_records, error_records):
    if not ctx.ok:
        return
    print_info("[Step 1] 錢包加值中...")
    code = await recharge_wallet_async(ctx.account)
    log_step_result(code, step="recharge_wallet", account=ctx.account, game_name=ctx.game_name)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "recharge_wallet",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
    else:
        step_success_records.append({
            "step": "recharge_wallet",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })


# Step 2: 建立 WS 並啟動接收
async def step_2_open_ws(ctx: TaskContext):
    if not ctx.ok:
        return
    print_info("[Step 2] 建立 WebSocket 連線中...")

    ws_url = f"{get_ws_base_url_by_game_type(ctx.game_type)}?token={ctx.token}&oid={ctx.oid}"
    print_info(f"🧪 WebSocket URL: {ws_url}")
    print_info(f"🧪 WebSocket Origin: {R88_GAME_WS_ORIGIN}")
    print_info(f"🧪 Token: {ctx.token}")

    code, ws = await open_ws_connection_task(ws_url, R88_GAME_WS_ORIGIN)
    log_step_result(code, step="open_ws", account=ctx.account, game_name=ctx.game_name)

    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        return

    # ✅ 初始化 WebSocket 對象與事件鎖
    ctx.ws = ws
    ctx.ws._join_event = asyncio.Event()        # 給 join_room 用
    ctx.ws.callback_done = asyncio.Event()      # ✅ 給 run_ws_step_async 等用的主流程鎖

    print_info(f"🧩 註冊時 ws id: {id(ctx.ws)}")  # debug

    # ✅ handler 註冊
    register_event_handler(ctx.ws, "join_room", handle_join_room_async)
    register_event_handler(ctx.ws, "keep_alive", handle_heartbeat_response)
    register_event_handler(ctx.ws, "bet", handle_bet_ack)
    register_event_handler(ctx.ws, "cur_round_finished", handle_round_finished_ack)
    register_event_handler(ctx.ws, "exit_room", handle_exit_room_ack)

    # ✅ debug 用：列出目前 handler 總表
    from workspace.tools.ws.ws_event_dispatcher_async import _ws_event_handlers
    print_info(f"🧩 dispatcher handler 註冊總表：{_ws_event_handlers.get(ctx.ws)}")

    # ✅ 啟動接收 loop
    asyncio.create_task(start_ws_async(ctx.ws))








# Step 3: 等待 join_room
async def step_3_wait_join_room(ctx: TaskContext):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 3] 等待 join_room 封包")
    try:
        await asyncio.wait_for(ctx.ws._join_event.wait(), timeout=10)
    except asyncio.TimeoutError:
        ctx.ok = False
        ctx.code = ResultCode.TASK_WS_TIMEOUT
        log_step_result(ctx.code, step="join_room_timeout", account=ctx.account, game_name=ctx.game_name)
        return

    log_step_result(ctx.ws.error_code, step="join_room", account=ctx.account, game_name=ctx.game_name)
    if ctx.ws.error_code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = ctx.ws.error_code




# Step 4: 發送 keep_alive
async def step_4_keep_alive(ctx: TaskContext, step_success_records, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 4] 發送 keep_alive 封包")
    code = await run_ws_step_async(
        ws_obj=ctx.ws,
        step_name="keep_alive",
        event_name="keep_alive",
        request_data={"event": "keep_alive"},
        step_success_records=step_success_records,
        error_records=error_records,
        ctx=ctx,  # ✅ 加這行
    )
    log_step_result(code, step="keep_alive", account=ctx.account, game_name=ctx.game_name)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
    else:
        step_success_records.append({
            "step": "keep_alive",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
#step 5發送bet封包        
async def step_5_send_bet(ctx: TaskContext, step_success_records, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 5] 發送 bet 封包")
    code = await send_bet_async(ctx.ws)
    log_step_result(code, step="send_bet", account=ctx.account, game_name=ctx.game_name)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "send_bet",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
    else:
        step_success_records.append({
            "step": "send_bet",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })

# Step 6: 等待 bet_ack 封包
async def step_6_bet_ack(ctx: TaskContext, step_success_records, error_records):
    if not ctx.ok or not ctx.ws:
        return

    print_info("[Step 6] 等待 bet_ack 封包")

    code = await run_ws_step_async(
        ws_obj=ctx.ws,
        step_name="bet_ack",
        event_name="bet",
        request_data={},  # ✅ 僅等待 bet 回應，不重送封包
        step_success_records=step_success_records,
        error_records=error_records,
        ctx=ctx,  # ✅ 傳入 ctx 讓錯誤記錄能包含帳號/遊戲資訊
    )

    log_step_result(code, step="bet_ack", account=ctx.account, game_name=ctx.game_name)

    if code != ResultCode.SUCCESS:
        print_info(f"[Debug] ❌ bet_ack 處理失敗，錯誤碼：{code}")
        ctx.ok = False
        ctx.code = code
    else:
        step_success_records.append({
            "step": "bet_ack",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })




# Step 7: 發送 cur_round_finished
async def step_7_round_finish(ctx: TaskContext, step_success_records, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 7] 發送 cur_round_finished 封包")
    code = await run_ws_step_async(
        ws_obj=ctx.ws,
        step_name="cur_round_finished",
        event_name="cur_round_finished",
        request_data={"event": "cur_round_finished"},
        step_success_records=step_success_records,
        error_records=error_records,
        ctx=ctx,  # ✅ 加這行
    )
    log_step_result(code, step="cur_round_finished", account=ctx.account, game_name=ctx.game_name)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "cur_round_finished",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
    else:
        step_success_records.append({
            "step": "cur_round_finished",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })


# Step 8: 發送 exit_room
async def step_8_exit_room(ctx: TaskContext, step_success_records, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 8] 發送 exit_room 封包")
    code = await run_ws_step_async(
        ws_obj=ctx.ws,
        step_name="exit_room",
        event_name="exit_room",
        request_data={"event": "exit_room"},
        step_success_records=step_success_records,
        error_records=error_records,
        ctx=ctx,  # ✅ 加這行
    )
    log_step_result(code, step="exit_room", account=ctx.account, game_name=ctx.game_name)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "exit_room",
            "account": ctx.account,
            "game_name": ctx.game_name,
            
        })
    else:
        step_success_records.append({
            "step": "exit_room",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
    clear_handlers(ctx.ws)





# === 主流程 ===
def ws_connection_flow(task_list, max_concurrency: int = 1):
    async def async_flow():


        error_records = []
        step_success_records = []
        contexts = [TaskContext(t) for t in task_list]

        await asyncio.gather(*[step_0_prepare(ctx) for ctx in contexts])
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