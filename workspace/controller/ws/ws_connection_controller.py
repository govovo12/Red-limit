"""
子控制器：處理單一帳號的 WebSocket 任務流程（建立連線 → 處理 join_room → keep_alive → bet → round_finished）
"""

# 📦 錯誤碼與環境設定
from workspace.tools.common.result_code import ResultCode
from workspace.tools.env.config_loader import R88_GAME_WS_BASE_URL, R88_GAME_WS_ORIGIN

# 🛠 工具模組
from workspace.tools.printer.printer import print_info
from workspace.tools.common.log_helper import log_simple_result
from workspace.tools.ws.ws_connection_async_helper import (
    close_ws_connection,
    start_ws_async,
)
from workspace.tools.ws.ws_event_dispatcher_async import (
    register_event_handler,
)

# 🔧 任務模組
from workspace.modules.task.recharge_wallet_task import recharge_wallet_async
from workspace.modules.ws.open_ws_connection_task import open_ws_connection_task
from workspace.modules.ws.handle_join_room_async import handle_join_room_async
from workspace.modules.ws.send_heartbeat_task import send_heartbeat_async, handle_heartbeat_response  # Step 4
from workspace.modules.ws.send_bet_task import send_bet_async  # Step 5
from workspace.modules.ws.parse.parse_bet_response import handle_bet_ack  # Step 5
from workspace.modules.ws.send_round_finished import send_round_finished_async, handle_round_finished_ack  # Step 6
from workspace.modules.ws.send_exit_room import send_exit_room_async, handle_exit_room_ack  # Step 7


import asyncio
from typing import Dict, List


async def handle_single_task_async(task: Dict, error_records: List[Dict], step_success_records: List[Dict]) -> int:
    """
    處理單一帳號的 WebSocket 流程，失敗紀錄將收集至 error_records，成功步驟記錄至 step_success_records
    """
    ws = None
    account = task.get("account")
    oid = task.get("oid")
    token = task.get("access_token")
    game_name = task.get("game_name")

    try:
        # Step 0
        if not account or not oid or not token:
            error_records.append({
                "code": ResultCode.INVALID_TASK,
                "step": "準備參數",
                "account": account,
                "game_name": game_name
            })
            return ResultCode.INVALID_TASK

        print_info(f"[Step 0] 📍 account={account}, oid={oid}")
        recharge_code = await recharge_wallet_async(account)
        if recharge_code != ResultCode.SUCCESS:
            error_records.append({
                "code": recharge_code,
                "step": "recharge_wallet",
                "account": account,
                "game_name": game_name
            })
            return recharge_code
        step_success_records.append({"step": "recharge_wallet", "account": account, "game_name": game_name})

        ws_url = f"{R88_GAME_WS_BASE_URL}?token={token}&oid={oid}"
        result_code, ws = await open_ws_connection_task(ws_url, R88_GAME_WS_ORIGIN)
        if result_code != ResultCode.SUCCESS or not ws:
            error_records.append({
                "code": result_code,
                "step": "open_ws",
                "account": account,
                "game_name": game_name
            })
            return result_code
        step_success_records.append({"step": "open_ws", "account": account, "game_name": game_name})

        await start_ws_async(ws)
        step_success_records.append({"step": "start_ws", "account": account, "game_name": game_name})

        try:
            await asyncio.wait_for(ws.callback_done.wait(), timeout=10)
        except asyncio.TimeoutError:
            error_records.append({
                "code": ResultCode.TASK_WS_TIMEOUT,
                "step": "join_room timeout",
                "account": account,
                "game_name": game_name
            })
            return ResultCode.TASK_WS_TIMEOUT

        if ws.error_code != ResultCode.SUCCESS:
            error_records.append({
                "code": ws.error_code,
                "step": "join_room",
                "account": account,
                "game_name": game_name
            })
            return ws.error_code
        step_success_records.append({"step": "join_room", "account": account, "game_name": game_name})

        # Step 4: keep_alive
        ws.callback_done = asyncio.Event()
        register_event_handler("keep_alive", handle_heartbeat_response)
        code = await send_heartbeat_async(ws)
        if code != ResultCode.SUCCESS:
            error_records.append({
                "code": code,
                "step": "keep_alive",
                "account": account,
                "game_name": game_name
            })
            return code
        try:
            await asyncio.wait_for(ws.callback_done.wait(), timeout=5)
        except asyncio.TimeoutError:
            error_records.append({
                "code": ResultCode.TASK_WS_TIMEOUT,
                "step": "keep_alive timeout",
                "account": account,
                "game_name": game_name
            })
            return ResultCode.TASK_WS_TIMEOUT
        if ws.error_code != ResultCode.SUCCESS:
            error_records.append({
                "code": ws.error_code,
                "step": "keep_alive",
                "account": account,
                "game_name": game_name
            })
            return ws.error_code
        step_success_records.append({"step": "keep_alive", "account": account, "game_name": game_name})

        # Step 5: bet
        ws.callback_done = asyncio.Event()
        register_event_handler("bet", handle_bet_ack)
        code = await send_bet_async(ws)
        if code != ResultCode.SUCCESS:
            error_records.append({
                "code": code,
                "step": "send_bet",
                "account": account,
                "game_name": game_name
            })
            return code
        try:
            await asyncio.wait_for(ws.callback_done.wait(), timeout=5)
        except asyncio.TimeoutError:
            error_records.append({
                "code": ResultCode.TASK_WS_TIMEOUT,
                "step": "bet timeout",
                "account": account,
                "game_name": game_name
            })
            return ResultCode.TASK_WS_TIMEOUT
        if ws.error_code != ResultCode.SUCCESS:
            error_records.append({
                "code": ws.error_code,
                "step": "bet_ack",
                "account": account,
                "game_name": game_name
            })
            if ws.error_code == ResultCode.TASK_BET_MISMATCHED:
                # 不中斷
                step_success_records.append({"step": "bet_ack (mismatched)", "account": account, "game_name": game_name})
                return ResultCode.SUCCESS
            return ws.error_code
        step_success_records.append({"step": "send_bet", "account": account, "game_name": game_name})

        # Step 6: cur_round_finished
        ws.callback_done = asyncio.Event()
        register_event_handler("cur_round_finished", handle_round_finished_ack)
        code = await send_round_finished_async(ws)
        if code != ResultCode.SUCCESS:
            error_records.append({
                "code": code,
                "step": "send_round_finished",
                "account": account,
                "game_name": game_name
            })
            return code
        try:
            await asyncio.wait_for(ws.callback_done.wait(), timeout=5)
        except asyncio.TimeoutError:
            error_records.append({
                "code": ResultCode.TASK_WS_TIMEOUT,
                "step": "round_finished timeout",
                "account": account,
                "game_name": game_name
            })
            return ResultCode.TASK_WS_TIMEOUT
        if ws.error_code != ResultCode.SUCCESS:
            error_records.append({
                "code": ws.error_code,
                "step": "round_finished_ack",
                "account": account,
                "game_name": game_name
            })
            return ws.error_code
        step_success_records.append({"step": "cur_round_finished", "account": account, "game_name": game_name})
        # Step 7: 發送 exit_room 封包
        print_info(f"[Step 7] 🚪 發送 exit_room")
        ws.callback_done = asyncio.Event()
        register_event_handler("exit_room", handle_exit_room_ack)

        code = await send_exit_room_async(ws)
        if code != ResultCode.SUCCESS:
            print_info(f"[Step 7 ❌] exit_room 發送失敗")
            error_records.append({
                "code": code,
                "step": "send_exit_room",
                "account": account,
                "game_name": game_name
            })
            return code

        try:
            await asyncio.wait_for(ws.callback_done.wait(), timeout=5)
        except asyncio.TimeoutError:
            print_info(f"[Step 7 ❌] exit_room callback 逾時")
            error_records.append({
                "code": ResultCode.TASK_WS_TIMEOUT,
                "step": "exit_room timeout",
                "account": account,
                "game_name": game_name
            })
            return ResultCode.TASK_WS_TIMEOUT

        if ws.error_code != ResultCode.SUCCESS:
            print_info(f"[Step 7 ❌] exit_room 回應錯誤")
            error_records.append({
                "code": ws.error_code,
                "step": "exit_room_ack",
                "account": account,
                "game_name": game_name
            })
            return ws.error_code

        print_info(f"[Step 7 ✅] exit_room 完成")
        step_success_records.append({"step": "exit_room", "account": account, "game_name": game_name})

        return ResultCode.SUCCESS

    except Exception:
        error_records.append({
            "code": ResultCode.TASK_EXCEPTION,
            "step": "exception",
            "account": account,
            "game_name": game_name
        })
        return ResultCode.TASK_EXCEPTION
    finally:
        if ws:
            await close_ws_connection(ws)


from collections import defaultdict  # 🔼 確保你在檔案開頭有加這個

def ws_connection_flow(task_list: List[dict], max_concurrency: int = 1) -> list:
    """
    子控制器流程：建立多條 WebSocket 並行連線，進行 join_room 驗證。
    最終統一印出錯誤摘要與「失敗任務中各步驟成功統計」。
    """
    register_event_handler("join_room", handle_join_room_async)

    async def async_flow():
        error_records = []
        step_success_records = []

        tasks = [handle_single_task_async(t, error_records, step_success_records) for t in task_list]
        results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r == ResultCode.SUCCESS)
        print_info(f"[Flow ✅] 全部完成，共成功 {success} 筆，失敗 {len(error_records)} 筆")

        if error_records:
            print_info("❌ 子控失敗清單如下：")
            for err in error_records:
                label = "⚠ WARNING" if err["code"] == ResultCode.TASK_BET_MISMATCHED else "❌ ERROR"
                print_info(f"{label} code={err['code']} | step={err['step']} | account={err['account']} | game={err['game_name']}")

            # 🔹 只列出失敗帳號中的成功步驟（分組印出）
            failed_accounts = {err['account'] for err in error_records}
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

        return [r for r in results if r != ResultCode.SUCCESS]

    return asyncio.run(async_flow())


