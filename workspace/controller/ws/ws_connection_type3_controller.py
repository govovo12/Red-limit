# 📦 錯誤碼與環境設定
from workspace.tools.common.result_code import ResultCode
from workspace.tools.env.config_loader import get_ws_base_url_by_game_type, R88_GAME_WS_ORIGIN

# 🛠 工具模組
from workspace.tools.ws.ws_connection_async_helper import close_ws_connection, start_ws_async
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.printer.printer import print_info
from workspace.tools.ws.ws_event_dispatcher_async import register_event_handler
from workspace.modules.tpye3_ws.verify_bet_rule_type3 import validate_bet_limit


# 🔧 任務模組
from workspace.modules.task.recharge_wallet_task import recharge_wallet_async
from workspace.modules.ws.open_ws_connection_task import open_ws_connection_task
from workspace.modules.tpye3_ws.verify_init_info_type3 import handle_init_info
from workspace.modules.tpye3_ws.verify_chip_limit_type3 import verify_chip_limit_from_packet


# 標準函式庫
import asyncio
from typing import Dict, List
from collections import defaultdict


async def handle_single_task_async(task: Dict, error_records: List[Dict], step_success_records: List[Dict]) -> int:
    """
    Type 3 子控制器：處理單一帳號的 WebSocket 任務流程（Step 0～4）
    """
    ws = None
    account = task.get("account")
    oid = task.get("oid")
    token = task.get("access_token")
    game_name = task.get("game_name")

    try:
        # Step 0: 接收主控參數
        print_info(f"📍 Step 0：接收主控參數")
        if not account or not oid or not token:
            code = ResultCode.INVALID_TASK
            log_step_result(code, step="prepare", account=account, game_name=game_name)
            return code

        # Step 1: 錢包加值
        print_info(f"🪙 Step 1：錢包加值")
        recharge_code = await recharge_wallet_async(account)
        if recharge_code != ResultCode.SUCCESS:
            log_step_result(recharge_code, step="recharge_wallet", account=account, game_name=game_name)
            return recharge_code
        log_step_result(recharge_code, step="recharge_wallet", account=account, game_name=game_name)
        step_success_records.append({"step": "recharge_wallet", "account": account, "game_name": game_name})

        # Step 2: 建立 WebSocket 連線
        print_info(f"🌐 Step 2：建立 WebSocket 連線")
        game_type = task.get("game_option_list_type")
        room_id = task.get("room_id")
        ws_base_url = get_ws_base_url_by_game_type(game_type)
        ws_url = f"{ws_base_url}?token={token}&oid={oid}"
        if room_id:
            ws_url += f"&room_no={room_id}"
        print_info(f"[DEBUG] WS 連線 URL = {ws_url}")

        result_code, ws = await open_ws_connection_task(ws_url, R88_GAME_WS_ORIGIN)
        if result_code != ResultCode.SUCCESS or not ws:
            log_step_result(result_code, step="open_ws", account=account, game_name=game_name)
            return result_code
        log_step_result(result_code, step="open_ws", account=account, game_name=game_name)
        step_success_records.append({"step": "open_ws", "account": account, "game_name": game_name})
        await start_ws_async(ws)

        # Step 3: 擷取封包 init_info
        print_info("🧩 Step 3：等待 init_info 封包")
        try:
            await asyncio.wait_for(ws.callback_done.wait(), timeout=8)
        except asyncio.TimeoutError:
            code = ResultCode.TASK_WS_TIMEOUT
            log_step_result(code, step="init_info timeout", account=account, game_name=game_name)
            return code

        if ws.error_code != ResultCode.SUCCESS:
            log_step_result(ws.error_code, step="init_info", account=account, game_name=game_name)
            return ws.error_code

        log_step_result(ws.error_code, step="init_info", account=account, game_name=game_name)
        step_success_records.append({"step": "init_info", "account": account, "game_name": game_name})

       # Step 4: 擷取限紅資訊與驗證（不再透過 ws 任務模組）
        print_info("🔍 Step 4：擷取限紅資訊與驗證")
        

        verify_code, bet_limit = verify_chip_limit_from_packet(ws.rs_data)

        if verify_code != ResultCode.SUCCESS:
            log_step_result(verify_code, step="verify_chip_limit", account=account, game_name=game_name)
            return verify_code

        log_step_result(verify_code, step="verify_chip_limit", account=account, game_name=game_name)
        step_success_records.append({
            "step": "verify_chip_limit",
            "account": account,
            "game_name": game_name,
            "bet_limit": bet_limit  # ✅ 可選：也把 bet_limit 存進去方便後續分析
})
        # Step 5:驗證線紅是否符合
        print_info("🧮 Step 5：比對限紅是否符合條件")
        validate_code = validate_bet_limit(bet_limit)

        if validate_code != ResultCode.SUCCESS:
            log_step_result(validate_code, step="verify_bet_rule", account=account, game_name=game_name)
            return validate_code

        log_step_result(validate_code, step="verify_bet_rule", account=account, game_name=game_name)
        step_success_records.append({
        "step": "verify_bet_rule",
        "account": account,
        "game_name": game_name
})
        # Step 6: 發送 exit_room 封包並等待回應（不驗內容）
        print_info("🚪 Step 6：發送 exit_room 封包（不驗回應內容）")

        from workspace.modules.tpye3_ws.handle_exit_room_type3 import (
        send_exit_room_async,
        handle_exit_room_ack,)
        from workspace.tools.ws.ws_event_dispatcher_async import register_event_handler

        # 註冊 exit_room 事件的 callback 處理器
        register_event_handler("exit_room", handle_exit_room_ack)

        # 發送封包
        exit_code = await send_exit_room_async(ws)
        if exit_code != ResultCode.SUCCESS:
            log_step_result(exit_code, step="send_exit_room", account=account, game_name=game_name)
            return exit_code

        # 等待伺服器回應 exit_room（不驗內容，只等 callback）
        try:
            await asyncio.wait_for(ws.callback_done.wait(), timeout=6)
        except asyncio.TimeoutError:
            log_step_result(ResultCode.TASK_WS_TIMEOUT, step="exit_room timeout", account=account, game_name=game_name)
            return ResultCode.TASK_WS_TIMEOUT

            # 成功收到回應（無論內容）
        log_step_result(ResultCode.SUCCESS, step="exit_room", account=account, game_name=game_name)
        step_success_records.append({
            "step": "exit_room",
            "account": account,
            "game_name": game_name
        })


        return ResultCode.SUCCESS

    except Exception:
        code = ResultCode.TASK_EXCEPTION
        log_step_result(code, step="exception", account=account, game_name=game_name)
        return code

    finally:
        if ws:
            await close_ws_connection(ws)


def ws_connection_flow(task_list: List[dict], max_concurrency: int = 1) -> list:
    """
    子控制器流程（Type 3）：建立多條 WebSocket 並行連線，執行前半段 Step 0～3。
    """
    register_event_handler("init_info", handle_init_info)  # ✅ 註冊放在最上方（與 Type 2 一致）

    async def async_flow():
        error_records = []
        step_success_records = []

        tasks = [handle_single_task_async(t, error_records, step_success_records) for t in task_list]
        results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r == ResultCode.SUCCESS)
        print_info(f"[Flow ✅] Type 3 全部完成，共成功 {success} 筆，失敗 {len(error_records)} 筆")

        if error_records:
            print_info("❌ Type 3 子控失敗清單如下：")
            for err in error_records:
                print_info(f"❌ code={err['code']} | step={err['step']} | account={err['account']} | game={err['game_name']}")

            # 額外統計：失敗帳號中完成的成功步驟
            failed_accounts = {e["account"] for e in error_records}
            grouped = defaultdict(list)
            for s in step_success_records:
                if s["account"] in failed_accounts:
                    grouped[(s["account"], s["game_name"])].append(s["step"])

            if grouped:
                print_info("\n📊 失敗任務中各步驟成功統計：")
                for (account, game), steps in grouped.items():
                    print_info(f"\n🔸 account={account} | game={game}")
                    for step in steps:
                        print_info(f"  ✅ {step}")

        return [r for r in results if r != ResultCode.SUCCESS]

    return asyncio.run(async_flow())
