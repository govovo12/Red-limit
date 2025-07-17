from workspace.modules.task.check_account_task import check_account_exists
from workspace.modules.task.unlock_wallet_task import unlock_wallet
from workspace.modules.task.recharge_wallet_task import recharge_wallet_async
from workspace.tools.env.config_loader import get_ws_base_url_by_type_key, R88_GAME_WS_ORIGIN
from workspace.tools.ws.ws_connection_async_helper import start_ws_async
from workspace.modules.type2_ws.open_ws_connection_task import open_ws_connection_task
from workspace.tools.ws.ws_event_handler_registry import auto_register_event_handlers
from workspace.modules.type3_ws.verify_chip_limit_type3 import verify_chip_limit
from workspace.modules.type3_ws.verify_bet_rule_type3 import validate_bet_limit
from workspace.modules.type2_ws.send_exit_room import send_exit_room_async
from workspace.tools.ws.ws_step_runner_async import run_ws_step_func_async
from workspace.modules.type3_ws.fallback_extract_bet_limit import extract_bet_limit_fallback

from workspace.tools.printer.printer import print_info
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.common.result_code import ResultCode
import asyncio
from collections import defaultdict
from typing import List
# ✅ 共用的上下文結構
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

# Step 0: 驗證參數
async def step_0_prepare(ctx: TaskContext, error_records):
    print_info(f"[Step 0] 接收主控參數 account={ctx.account}, oid={ctx.oid}, game={ctx.game_name}")
    if not ctx.account or not ctx.oid or not ctx.token:
        ctx.ok = False
        ctx.code = ResultCode.INVALID_TASK
        log_step_result(ctx.code, step="prepare", account=ctx.account, game_name=ctx.game_name)
        error_records.append({
            "code": ctx.code,
            "step": "prepare",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })

# Step 0.5: 查 pf_account
async def step_0_5_check_account(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info(f"[Step 0.5] 對應 pf_account 中... | account={ctx.account} | game={ctx.game_name}")


    code, pf_account = await check_account_exists(ctx.account)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "check_account",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
    else:
        ctx.pf_account = pf_account
        print_info(f"[Step 0.5] ✅ pf_account 對應成功：{pf_account} | account={ctx.account} | game={ctx.game_name}")


# Step 0.6: 解鎖錢包
async def step_0_6_unlock_wallet(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info(f"[Step 0.6] 解鎖帳號中... | account={ctx.account} | game={ctx.game_name}")


    code = await unlock_wallet(ctx.pf_account)
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "unlock_wallet",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
    else:
        print_info(f"[Step 0.6] ✅ 解鎖成功 | account={ctx.account} | game={ctx.game_name}")


# Step 1: 錢包加值
async def step_1_recharge_wallet(ctx: TaskContext, error_records):
    if not ctx.ok:
        return
    print_info(f"[Step 1] 執行加值任務中... | account={ctx.account} | game={ctx.game_name}")


    code = await recharge_wallet_async(ctx.account)
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
        print_info(f"[Step 1] ✅ 加值成功 | account={ctx.account} | game={ctx.game_name}")


# Step 2：建立 WebSocket 並綁定事件（type 3）
async def step_2_open_ws(ctx: TaskContext, error_records):
    if not ctx.ok:
        return

    print_info(f"[Step 2] 建立 WebSocket 中... | account={ctx.account} | game={ctx.game_name}")


    ws_base_url = get_ws_base_url_by_type_key(ctx.game_type)
    ws_url = f"{ws_base_url}?token={ctx.token}&oid={ctx.oid}"

    room_id = ctx.task.get("room_id")
    if room_id:
        ws_url += f"&room_no={room_id}"

    print_info(f"[DEBUG] ws_url={ws_url}")
    code, ws = await open_ws_connection_task(ws_url, R88_GAME_WS_ORIGIN)

    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "open_ws",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
        return

    ctx.ws = ws
    ctx.ws.callback_done = asyncio.Event()
    ctx.ws.account = ctx.account
    ctx.ws.game_name = ctx.game_name

    auto_register_event_handlers(ctx.ws, flow_type="type3")
    asyncio.create_task(start_ws_async(ctx.ws))
    print_info("[Step 2] ✅ WebSocket 連線成功，等待封包中...")


# Step 3: 等待 init_info 封包（with timeout）
async def step_3_wait_init_info(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info(f"[Step 3] 等待封包資料傳入中... | account={ctx.account} | game={ctx.game_name}")

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

    code = ctx.ws.error_code
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "init_info",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
# Step 4: 擷取限紅資訊
async def step_4_parse_chip_limit(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info(f"[Step 4] 擷取限紅資料中... | account={ctx.account} | game={ctx.game_name}")

    ctx.ws.pf_account = ctx.pf_account

    code = await verify_chip_limit(ctx.ws)

    # ✅ 如果主模組失敗，自動切換 fallback
    if code == ResultCode.TASK_LIMIT_EXTRACTION_FAILED:
        print_info("[Step 4] 🌀 限紅擷取失敗，切換 fallback 模組...")
        code = await extract_bet_limit_fallback(ctx.ws)

    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "verify_chip_limit",
            "account": ctx.account,
            "game_name": ctx.game_name,
            "oid": ctx.oid,
        })
    else:
        print_info(f"[Step 4] ✅ 成功擷取限紅：{ctx.ws.bet_limit}")





# Step 5: 驗證限紅是否合規
async def step_5_validate_bet_limit(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws or not hasattr(ctx.ws, "bet_limit"):
        return
    print_info(f"[Step 5] 驗證限紅是否合法... | account={ctx.account} | game={ctx.game_name}")


    code = await validate_bet_limit(ctx.ws.bet_limit)

    if code != ResultCode.SUCCESS:
        ctx.ok = False
        ctx.code = code
        error_records.append({
            "code": code,
            "step": "validate_bet_limit",
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
    else:
        print_info(f"[Step 5] ✅ 限紅驗證通過：{ctx.ws.bet_limit}")
# Step 6: 離開遊戲
async def step_6_send_exit_room(ctx: TaskContext, error_records):
    if not ctx.ok or not ctx.ws:
        return
    print_info(f"[Step 6] 離開遊戲... | account={ctx.account} | game={ctx.game_name}")


    code = await run_ws_step_func_async(ctx.ws, send_exit_room_async, timeout=5)

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
        print_info("[Step 6] ✅ 成功離開遊戲")

# ✅ 子控制器：目前僅執行 Step 0～1（type3 基礎版本）
def ws_connection_flow(task_list: List[dict], max_concurrency: int = 1) -> list:
    async def async_flow():
        step_success_records = []
        error_records = []
        contexts = [TaskContext(task) for task in task_list]

        await asyncio.gather(*[step_0_prepare(ctx, error_records) for ctx in contexts])
        await asyncio.gather(*[step_0_5_check_account(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_0_6_unlock_wallet(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_1_recharge_wallet(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_2_open_ws(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_3_wait_init_info(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_4_parse_chip_limit(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_5_validate_bet_limit(ctx, error_records) for ctx in contexts if ctx.ok])
        await asyncio.gather(*[step_6_send_exit_room(ctx, error_records) for ctx in contexts if ctx.ok])

        failed_accounts = {err['account'] for err in error_records if 'account' in err}

        success = 0
        fail = 0
        for ctx in contexts:
            account = getattr(ctx, "account", None)
            if account in failed_accounts:
                fail += 1
            else:
                success += 1

        print_info(f"[Flow ✅] Type 3 全部完成，共成功 {success} 筆，失敗 {fail} 筆")

        if error_records:
            print_info("❌ Type 3 子控失敗清單如下：")
            for err in error_records:
                print_info(f"❌ code={err['code']} | step={err['step']} | account={err['account']} | game={err['game_name']} | oid={err.get('oid')}")


            # 📊 額外統計：失敗任務中，哪些步驟有成功
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

        return [ctx.code for ctx in contexts if not ctx.ok]  # ✅ 回傳錯誤碼列表

    return asyncio.run(async_flow())  # ✅ 放在 def 外層，return 結果


