# workspace/modules/type2_ws/ws_connection_type2_controller.py

import asyncio
from collections import defaultdict

# === 錯誤碼與工具 ===
from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.env.config_loader import get_ws_base_url_by_type_key, R88_GAME_WS_ORIGIN
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.ws.ws_connection_async_helper import start_ws_async
from workspace.tools.ws.ws_event_handler_registry import auto_register_event_handlers
from workspace.tools.ws.ws_step_runner_async import run_ws_step_func_async, run_ws_send_and_wait_async
from workspace.tools.ws.report_helper import report_step_result
from workspace.tools.format.alignment_helper import pad_display_width
from workspace.tools.format.stat_formatter import format_stat_lines

# === 任務模組 ===
from workspace.modules.task.unlock_wallet_task import unlock_wallet
from workspace.modules.task.check_account_task import check_account_exists
from workspace.modules.task.recharge_wallet_task import recharge_wallet_async
from workspace.modules.type2_ws.open_ws_connection_task import open_ws_connection_task
from workspace.modules.type2_ws.send_heartbeat_task import send_heartbeat_async
from workspace.modules.type2_ws.send_bet_task import send_bet_async
from workspace.modules.type2_ws.send_round_finished import send_round_finished_async
from workspace.modules.type2_ws.send_exit_room import send_exit_room_async
from workspace.modules.type2_ws.assemble_stat_type2 import assemble_stat

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
        self.stat = None
        self.pf_account = None
        self.all_codes = []
        self.step_code_map = {}  # ✅ 關鍵補上這行

    def __str__(self):
        return f"game_name={self.game_name} | account={self.account}"

        

# Step 0: 驗證參數
async def step_0_prepare(ctx: TaskContext):
    print_info(f"[Step 0] 接收主控參數 game={ctx.game_name} account={ctx.account}", ctx=ctx)
    if not ctx.account or not ctx.oid or not ctx.token:
        ctx.ok = False
        ctx.code = ResultCode.INVALID_TASK
        log_step_result(ctx.code, step="prepare", account=ctx.account, game_name=ctx.game_name)
        return
    
    log_step_result(ResultCode.SUCCESS, step="prepare", account=ctx.account, game_name=ctx.game_name)


# Step 1: 查 pf_account
async def step_1_check_account(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info(f"[Step 1] 查詢 pf_account game={ctx.game_name} account={ctx.account}", ctx=ctx)

    code, pf_account = await check_account_exists(ctx.account)
    ctx.code = code
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        error_records.append({
            "code": code,
            "step": "check_account",
            "account": ctx.account,
            "game_name": ctx.game_name
        })
        log_step_result(code, step="check_account", account=ctx.account, game_name=ctx.game_name)
        return

    ctx.pf_account = pf_account
    
    log_step_result(code, step="check_account", account=ctx.account, game_name=ctx.game_name)


# Step 2: 解鎖錢包
async def step_2_unlock_wallet(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info(f"[Step 2] 解鎖錢包 game={ctx.game_name} account={ctx.account}", ctx=ctx)

    code = await unlock_wallet(ctx.pf_account)
    ctx.code = code
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        error_records.append({
            "code": code,
            "step": "unlock_wallet",
            "account": ctx.account,
            "game_name": ctx.game_name
        })
        log_step_result(code, step="unlock_wallet", account=ctx.account, game_name=ctx.game_name)
        return

    
    log_step_result(code, step="unlock_wallet", account=ctx.account, game_name=ctx.game_name)


# Step 3: 加值
async def step_3_recharge_wallet(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info(f"[Step 3] 加值 game={ctx.game_name} account={ctx.account}", ctx=ctx)

    code = await recharge_wallet_async(ctx.account)
    ctx.code = code
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        error_records.append({
            "code": code,
            "step": "recharge_wallet",
            "account": ctx.account,
            "game_name": ctx.game_name
        })
        log_step_result(code, step="recharge_wallet", account=ctx.account, game_name=ctx.game_name)
        return

    
    log_step_result(code, step="recharge_wallet", account=ctx.account, game_name=ctx.game_name)


# Step 4: 建立 WebSocket
async def step_4_open_ws(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info(f"[Step 4] 建立 WebSocket game={ctx.game_name} account={ctx.account}", ctx=ctx)

    ws_url = f"{get_ws_base_url_by_type_key(f'type_{ctx.game_type}')}?token={ctx.token}&oid={ctx.oid}"
    ctx.code, ws = await open_ws_connection_task(ws_url, R88_GAME_WS_ORIGIN)
    if ctx.code != ResultCode.SUCCESS:
        ctx.ok = False
        error_records.append({
            "code": ctx.code,
            "step": "open_ws",
            "account": ctx.account,
            "game_name": ctx.game_name
        })
        log_step_result(ctx.code, step="open_ws", account=ctx.account, game_name=ctx.game_name)
        return

    ctx.ws = ws
    ctx.ws._join_event = asyncio.Event()
    ctx.ws.account = ctx.account
    ctx.ws.game_name = ctx.game_name

    auto_register_event_handlers(ctx.ws, flow_type="type2")
    asyncio.create_task(start_ws_async(ctx.ws))

    
    log_step_result(ctx.code, step="open_ws", account=ctx.account, game_name=ctx.game_name)


# Step 5: 等 join_room
async def step_5_wait_join_room(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info(f"[Step 5] 等待 join_room 封包 game={ctx.game_name} account={ctx.account}", ctx=ctx)

    try:
        await asyncio.wait_for(ctx.ws._join_event.wait(), timeout=10)
    except asyncio.TimeoutError:
        ctx.ok = False
        ctx.code = ResultCode.TASK_WS_TIMEOUT
        error_records.append({
            "code": ctx.code,
            "step": "join_room_timeout",
            "account": ctx.account,
            "game_name": ctx.game_name
        })
        log_step_result(ctx.code, step="join_room_timeout", account=ctx.account, game_name=ctx.game_name)
        return

    ctx.code = ctx.ws.error_code
    if ctx.code != ResultCode.SUCCESS:
        ctx.ok = False
        error_records.append({
            "code": ctx.code,
            "step": "join_room",
            "account": ctx.account,
            "game_name": ctx.game_name
        })
        log_step_result(ctx.code, step="join_room", account=ctx.account, game_name=ctx.game_name)
        return

    
    log_step_result(ctx.code, step="join_room", account=ctx.account, game_name=ctx.game_name)



# Step 6: keep_alive
async def step_6_keep_alive(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return

    print_info(f"[Step 6] 發送 keep_alive 封包 game={ctx.game_name} account={ctx.account}", ctx=ctx)

    ctx.ws.callback_done = asyncio.Event()
    code = await run_ws_step_func_async(ctx.ws, send_heartbeat_async)
    ctx.code = code
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        error_records.append({
            "code": code,
            "step": "keep_alive",
            "account": ctx.account,
            "game_name": ctx.game_name
        })
        log_step_result(code, step="keep_alive", account=ctx.account, game_name=ctx.game_name)
        return

    
    log_step_result(code, step="keep_alive", account=ctx.account, game_name=ctx.game_name)


# Step 7: 發送 bet 並等待伺服器回應
async def step_7_send_bet_and_wait(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return

    print_info(f"[Step 7] 發送 bet 封包 game={ctx.game_name} account={ctx.account}", ctx=ctx)
    ctx.ws.callback_done = asyncio.Event()

    # ✅ 檢查 bet_context 是否存在
    if not getattr(ctx.ws, "bet_context", None):
        report_step_result(
            ctx,
            ResultCode.TASK_BET_CONTEXT_MISSING,
            step="bet_ack",
            error_records=error_records
        )
        return

    # ✅ 發送封包，等待任務模組 handle_bet_ack 處理封包與驗證
    code = await run_ws_send_and_wait_async(ctx.ws, send_bet_async, payload=ctx.ws.bet_context)

    # ✅ 從 ws.bet_result 取出值，轉拷進 ctx（給 Step 8 統計使用）
    result = getattr(ctx.ws, "bet_result", {}) or {}
    ctx.expect = result.get("rule") 
    ctx.actual = result.get("actual")
    ctx.code = result.get("error_code")

    # ✅ 統一報錯、記錄錯誤
    report_step_result(
        ctx,
        code,
        step="bet_ack",
        error_records=error_records
    )

    if code == ResultCode.SUCCESS:
        print_info(f"[Step 7] bet 封包成功 game={ctx.game_name} account={ctx.account}", ctx=ctx)


# ✅ Step 8：組合限紅統計報表（不參與錯誤碼記錄）
async def step_8_assemble_stat(ctx: TaskContext, error_records: list[int]) -> None:
    if not ctx.ok:
        return

    print_info(f"[Step 8] 組合限紅統計報表 game={ctx.game_name} account={ctx.account}", ctx=ctx)

    data = {
        "game": ctx.game_name,
        "account": ctx.account,
        "expect": ctx.expect,
        "actual": ctx.actual,
        "code": ctx.code,
    }

    stat, _ = assemble_stat(data)
    ctx.stat = stat  # ✅ 僅記錄報表資料，不再影響錯誤判定

    

# Step 9: cur_round_finished
async def step_9_round_finish(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return

    print_info(f"[Step 9] 發送 cur_round_finished 封包 game={ctx.game_name} account={ctx.account}", ctx=ctx)

    ctx.ws.callback_done = asyncio.Event()
    code = await run_ws_step_func_async(ctx.ws, send_round_finished_async)
    ctx.code = code
    ctx.all_codes.append(code)
    if code != ResultCode.SUCCESS:
        report_step_result(ctx, code, step="cur_round_finished", error_records=error_records)
        return

    
    report_step_result(ctx, code, step="cur_round_finished", error_records=error_records)


# Step 10: exit_room
async def step_10_exit_room(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return

    print_info(f"[Step 10] 發送 exit_room 封包 game={ctx.game_name} account={ctx.account}", ctx=ctx)

    code = await run_ws_step_func_async(ctx.ws, send_exit_room_async)
    ctx.code = code
    ctx.all_codes.append(code)
    if code != ResultCode.SUCCESS:
        report_step_result(ctx, code, step="exit_room", error_records=error_records)
        return

    
    report_step_result(ctx, code, step="exit_room", error_records=error_records)


# === 主流程 ===
def ws_connection_flow(task_list, max_concurrency: int = 1):
    async def async_flow():
        error_records = []
        contexts = [TaskContext(t) for t in task_list]

        await asyncio.gather(*[step_0_prepare(ctx) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_1_check_account(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_2_unlock_wallet(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_3_recharge_wallet(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_4_open_ws(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_5_wait_join_room(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_6_keep_alive(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_7_send_bet_and_wait(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_8_assemble_stat(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_9_round_finish(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_10_exit_room(ctx, error_records) for ctx in contexts if ctx.ok])

        # === 統計失敗帳號 ===
        failed_accounts = {
            ctx.account for ctx in contexts
            if any(code != ResultCode.SUCCESS for code in ctx.step_code_map.values())
        }

        success = 0
        fail = 0
        for ctx in contexts:
            if ctx.account in failed_accounts:
                fail += 1
            else:
                success += 1

        print_info(f"[Flow ✅] 全部完成，共成功 {success} 筆，失敗 {fail} 筆")

        # === 印出錯誤碼列表 ===
        if failed_accounts:
            print_info("📦 type_2 子控執行完成，錯誤碼列表如下（非 0）：")
            for ctx in contexts:
                for step, code in ctx.step_code_map.items():
                    if code != ResultCode.SUCCESS:
                        print_info(f"⛔ account={ctx.account} game={ctx.game_name} step={step} code={code}")

        # ✅ 回傳報表資料給總控
        stat_dicts = [ctx.stat for ctx in contexts if isinstance(ctx.stat, dict)]
        return {"type_2": stat_dicts}


    return asyncio.run(async_flow())


    




