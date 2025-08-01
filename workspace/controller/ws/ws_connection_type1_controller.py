# === 系統與類型支援 ===
import asyncio
import os
from typing import List

# === 任務模組（共通功能） ===
from workspace.modules.task.check_account_task import check_account_exists
from workspace.modules.task.unlock_wallet_task import unlock_wallet
from workspace.modules.task.recharge_wallet_task import recharge_wallet_async

# === 任務模組（Type 2 專用） ===
from workspace.modules.type2_ws.open_ws_connection_task import open_ws_connection_task

# === 任務模組（共通封裝工具） ===
from workspace.tools.ws.ws_event_handler_registry import auto_register_event_handlers
from workspace.tools.ws.ws_connection_async_helper import start_ws_async
from workspace.tools.env.config_loader import get_ws_base_url_by_type_key, R88_GAME_WS_ORIGIN

# === 印出與錯誤碼管理 ===
from workspace.tools.printer.printer import print_info
from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.log_helper import log_step_result

# === 任務模組（Type 1 專用） ===
from workspace.modules.type1_ws.verify_chip_limit_standard_type1 import verify_chip_limit
from workspace.modules.type1_ws.fallback_extract_bet_limit_type1 import extract_bet_limit_fallback
from workspace.modules.type1_ws.verify_bet_rule_type1 import validate_bet_limit_type1
from workspace.modules.type1_ws.handle_exit_room_type1 import send_exit_room_async
from workspace.modules.type1_ws.assemble_stat_type1 import assemble_stat


class TaskContext:
    def __init__(self, task):
        self.task = task
        self.account = task.get("account")
        self.oid = task.get("oid")
        self.token = task.get("access_token")
        self.game_name = task.get("game_name")
        self.game_type = task.get("type")
        self.ws = None
        self.ok = True
        self.code = None
        self.pf_account = None
        self.stat = None  # 🔸 新增：統計資料欄位，預設為 None


# Step 0: 檢查參數
async def step_0_prepare(ctx: TaskContext, error_records):
    print_info(f"[Step 0] 接收主控參數 account={ctx.account}, oid={ctx.oid}, game={ctx.game_name}", ctx=ctx, game_type=ctx.game_type)
    if not ctx.account or not ctx.oid or not ctx.token:
        ctx.ok = False
        ctx.code = ResultCode.INVALID_TASK
        log_step_result(ctx.code, step="prepare", account=ctx.account, game_name=ctx.game_name)
        error_records.append({"code": ctx.code, "step": "prepare", "account": ctx.account, "game_name": ctx.game_name})


# Step 0.5: 查 pf_account
async def step_0_5_check_account(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info("[Step 0.5] 查詢 pf_account 對應關係中...", ctx=ctx, game_type=ctx.game_type)
    code, pf_account = await check_account_exists(ctx.account)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({"code": code, "step": "check_account", "account": ctx.account, "game_name": ctx.game_name})
    else:
        ctx.pf_account = pf_account
        print_info(f"[Step 0.5] ✅ pf_account 對應成功：{pf_account}", ctx=ctx, game_type=ctx.game_type)


# Step 0.6: 解鎖錢包
async def step_0_6_unlock_wallet(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info("[Step 0.6] 嘗試解鎖錢包...", ctx=ctx, game_type=ctx.game_type)
    code = await unlock_wallet(ctx.pf_account)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({"code": code, "step": "unlock_wallet", "account": ctx.account, "game_name": ctx.game_name})
    else:
        print_info("[Step 0.6] ✅ 錢包已成功解鎖", ctx=ctx, game_type=ctx.game_type)


# Step 1: 錢包加值
async def step_1_recharge_wallet(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info("[Step 1] 錢包加值中...", ctx=ctx, game_type=ctx.game_type)
    code = await recharge_wallet_async(ctx.account)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({"code": code, "step": "recharge_wallet", "account": ctx.account, "game_name": ctx.game_name})
    else:
        print_info("[Step 1] ✅ 加值成功", ctx=ctx, game_type=ctx.game_type)


# Step 2: 建立 WebSocket 並綁定事件
async def step_2_open_ws(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info("[Step 2] 建立 WebSocket 連線中...", ctx=ctx, game_type=ctx.game_type)
    ws_base_url = get_ws_base_url_by_type_key(ctx.game_type)
    ws_url = f"{ws_base_url}?token={ctx.token}&oid={ctx.oid}"
    room_id = ctx.task.get("room_id")
    if room_id:
        ws_url += f"&room_no={room_id}"
    print_info(f"[DEBUG] ws_url={ws_url}", ctx=ctx, game_type=ctx.game_type)
    code, ws = await open_ws_connection_task(ws_url, R88_GAME_WS_ORIGIN)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({"code": code, "step": "open_ws", "account": ctx.account, "game_name": ctx.game_name})
        return
    ctx.ws = ws
    ctx.ws.callback_done = asyncio.Event()
    ctx.ws.account = ctx.account
    ctx.ws.game_name = ctx.game_name
    auto_register_event_handlers(ctx.ws, flow_type="type1")
    asyncio.create_task(start_ws_async(ctx.ws))
    print_info("[Step 2] ✅ WebSocket 連線成功，等待封包中...", ctx=ctx, game_type=ctx.game_type)


# Step 3: 等待 init_info
async def step_3_wait_init_info(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 3] 等待 init_info 封包", ctx=ctx, game_type=ctx.game_type)
    try:
        await asyncio.wait_for(ctx.ws.callback_done.wait(), timeout=10)
    except asyncio.TimeoutError:
        ctx.ok = False
        ctx.code = ResultCode.TASK_WS_TIMEOUT
        error_records.append({
            "code": ctx.code,
            "step": "init_info_timeout",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
        return

    if ctx.ws.error_code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = ctx.ws.error_code
        error_records.append({
            "code": ctx.code,
            "step": "init_info",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })


# Step 4: 擷取限紅（恢復原來的邏輯，不進行統計）
async def step_4_verify_chip_limit(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return

    print_info("[Step 4] 擷取限紅中...", ctx=ctx, game_type=ctx.game_type)
    code = await verify_chip_limit(ctx.ws)
    if code != ResultCode.SUCCESS:
        print_info("[Step 4] 標準擷取失敗，啟動 fallback...", ctx=ctx, game_type=ctx.game_type)
        code = await extract_bet_limit_fallback(ctx.ws)

    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "verify_chip_limit",
            "account": ctx.account,
            "game_name": ctx.game_name
        })
    else:
        print_info(f"[Step 4] ✅ 擷取成功：限紅 = {ctx.ws.bet_limit}", ctx=ctx, game_type=ctx.game_type)


# Step 5：驗證限紅
async def step_5_validate_bet_limit(ctx: TaskContext, error_records):
    print_info(f"[Step 5] 驗證限紅是否符合...", ctx=ctx, game_type=ctx.game_type)

    # 呼叫任務模組，取得錯誤碼、規則、實際限紅
    code, rule, bet_limit = await validate_bet_limit_type1(ctx.ws.bet_limit)

    # ✅ 將值儲存進 ctx，交由後續 step_6 組裝 ctx.stat
    ctx.code = code
    ctx.expect = rule
    ctx.actual = bet_limit

    if code != ResultCode.SUCCESS:
        ctx.ok = False

        # 統一錯誤記錄與錯誤碼彙整
        log_step_result(code, step="validate_bet_limit", account=ctx.account, game_name=ctx.game_name)

        error_records.append({
            "code": code,
            "step": "validate_bet_limit",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
    else:
        print_info(f"[Step 5] ✅ 限紅驗證通過：{bet_limit}", ctx=ctx, game_type=ctx.game_type)


# Step 6：組裝限紅報表格式
async def step_6_assemble_stat(ctx: TaskContext, error_records):
    # 💡 不檢查 ctx.ok
    print_info("[Step 6] 組裝限紅驗證報表格式")

    stat, _ = assemble_stat({
        "account": ctx.account,
        "game": ctx.game_name,
        "expect": getattr(ctx, "expect", None),
        "actual": getattr(ctx, "actual", None),
        "code": getattr(ctx, "code", ResultCode.TASK_EXCEPTION),
    })

    ctx.stat = stat


# Step 7: 離開房間
async def step_7_exit_room(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info("[Step 7] 發送 exit_room 封包...", ctx=ctx, game_type=ctx.game_type)
    code = await send_exit_room_async(ctx.ws)
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
        print_info("[Step 7] ✅ exit_room 發送成功", ctx=ctx, game_type=ctx.game_type)


# 子控主流程
def ws_connection_flow(task_list: List[dict], max_concurrency: int = 1) -> list:
    async def async_flow():
        error_records = []
        contexts = [TaskContext(task) for task in task_list]

        # === 步驟執行區 ===
        await asyncio.gather(*(step_0_prepare(ctx, error_records) for ctx in contexts))
        await asyncio.gather(*(step_0_5_check_account(ctx, error_records) for ctx in contexts if ctx.ok))
        await asyncio.gather(*(step_0_6_unlock_wallet(ctx, error_records) for ctx in contexts if ctx.ok))
        await asyncio.gather(*(step_1_recharge_wallet(ctx, error_records) for ctx in contexts if ctx.ok))
        await asyncio.gather(*(step_2_open_ws(ctx, error_records) for ctx in contexts if ctx.ok))
        await asyncio.gather(*(step_3_wait_init_info(ctx, error_records) for ctx in contexts if ctx.ok))
        await asyncio.gather(*(step_4_verify_chip_limit(ctx, error_records) for ctx in contexts if ctx.ok))
        await asyncio.gather(*(step_5_validate_bet_limit(ctx, error_records) for ctx in contexts if ctx.ok))
        await asyncio.gather(*(step_6_assemble_stat(ctx, error_records) for ctx in contexts))
        await asyncio.gather(*(step_7_exit_room(ctx, error_records) for ctx in contexts if ctx.ok))

        # === 統計成功失敗筆數 ===
        failed_accounts = {err['account'] for err in error_records if 'account' in err}
        success = 0
        fail = 0
        for ctx in contexts:
            if ctx.account in failed_accounts:
                fail += 1
            else:
                success += 1

        print_info(f"[Flow ☑] Type 1 全部完成，共成功 {success} 筆，失敗 {fail} 筆")

        # === 錯誤統計印出 ===
        if error_records:
            print_info("❌ type_1 子控有錯誤發生，錯誤碼彙整如下（非 0）：")
            for err in error_records:
                code = err.get("code")
                step = err.get("step")
                acc = err.get("account", "N/A")
                game = err.get("game_name", "N/A")
                print_info(f"code={code} step={step} account={acc} game={game}")

        
        # ✅ 對成功帳號執行格式化報表
        stat_dicts = [ctx.stat for ctx in contexts if ctx.stat]

        # ✅ 確保回傳的 type_key 格式正確（避免出現 type_type_1）
        type_key = contexts[0].game_type
        type_key = type_key if type_key.startswith("type_") else f"type_{type_key}"

        return {type_key: stat_dicts}


    return asyncio.run(async_flow())


