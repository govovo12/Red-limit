"""
子控制器：處理單一帳號的 WebSocket 任務流程（建立連線 → 處理 join_room → keep_alive → bet → round_finished）
"""

# 📦 錯誤碼與環境設定
from workspace.tools.common.result_code import ResultCode
from workspace.tools.env.config_loader import get_ws_base_url_by_game_type, R88_GAME_WS_ORIGIN
# 🛠 工具模組
from workspace.tools.printer.printer import print_info
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.ws.ws_connection_async_helper import close_ws_connection, start_ws_async
from workspace.tools.ws.ws_event_dispatcher_async import register_event_handler
from workspace.tools.ws.ws_step_runner_async import run_ws_step_async

# 🔧 任務模組
from workspace.modules.task.recharge_wallet_task import recharge_wallet_async
from workspace.modules.ws.open_ws_connection_task import open_ws_connection_task
from workspace.modules.ws.handle_join_room_async import handle_join_room_async
from workspace.modules.ws.send_heartbeat_task import send_heartbeat_async, handle_heartbeat_response
from workspace.modules.ws.send_bet_task import send_bet_async
from workspace.modules.ws.parse.parse_bet_response import handle_bet_ack
from workspace.modules.ws.send_round_finished import send_round_finished_async, handle_round_finished_ack
from workspace.modules.ws.send_exit_room import send_exit_room_async, handle_exit_room_ack

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
        # Step 0: 接收主控參數
        print_info("🟢 Step 0: 接收主控參數")
        if not account or not oid or not token:
            code = ResultCode.INVALID_TASK
            log_step_result(code, step="prepare", account=account, game_name=game_name)
            return code

        # Step 1: 錢包加值
        print_info("🟢 Step 1: 錢包加值")
        recharge_code = await recharge_wallet_async(account)
        if recharge_code != ResultCode.SUCCESS:
            log_step_result(recharge_code, step="recharge_wallet", account=account, game_name=game_name)
            return recharge_code
        log_step_result(recharge_code, step="recharge_wallet", account=account, game_name=game_name)
        step_success_records.append({"step": "recharge_wallet", "account": account, "game_name": game_name})

        # Step 2: 組合連線參數 + 建立 WebSocket 連線
        game_type = task.get("game_option_list_type")  # 👈 來自快取中的欄位
        ws_base_url = get_ws_base_url_by_game_type(game_type)
        ws_url = f"{ws_base_url}?token={token}&oid={oid}"
        result_code, ws = await open_ws_connection_task(ws_url, R88_GAME_WS_ORIGIN)
        if result_code != ResultCode.SUCCESS or not ws:
            log_step_result(result_code, step="open_ws", account=account, game_name=game_name)
            return result_code
        log_step_result(result_code, step="open_ws", account=account, game_name=game_name)
        step_success_records.append({"step": "open_ws", "account": account, "game_name": game_name})

        # Step 3: 啟動 WS 接收封包循環 + 等待 join_room
        print_info("🟢 Step 3: 啟動封包接收循環 + 等待 join_room")
        await start_ws_async(ws)
        log_step_result(ResultCode.SUCCESS, step="start_ws", account=account, game_name=game_name)
        step_success_records.append({"step": "start_ws", "account": account, "game_name": game_name})

        try:
            await asyncio.wait_for(ws.callback_done.wait(), timeout=10)
        except asyncio.TimeoutError:
            code = ResultCode.TASK_WS_TIMEOUT
            log_step_result(code, step="join_room_timeout", account=account, game_name=game_name)
            return code

        if ws.error_code != ResultCode.SUCCESS:
            log_step_result(ws.error_code, step="join_room", account=account, game_name=game_name)
            return ws.error_code
        log_step_result(ResultCode.SUCCESS, step="join_room", account=account, game_name=game_name)
        step_success_records.append({"step": "join_room", "account": account, "game_name": game_name})

        # Step 4: 發送 keep_alive 並驗證回應
        print_info("🟢 Step 4: 發送 keep_alive 並驗證回應")
        code = await run_ws_step_async(
            ws=ws,
            event_name="keep_alive",
            handler_func=handle_heartbeat_response,
            send_func=send_heartbeat_async,
            timeout_sec=5,
            step_label="keep_alive",
            account=account,
            game_name=game_name,
            step_success_records=step_success_records,
            error_records=error_records,
        )
        log_step_result(code, step="keep_alive", account=account, game_name=game_name)
        if code != ResultCode.SUCCESS:
            return code

        # Step 5: 發送 bet 並驗證 ack
        print_info("🟢 Step 5: 發送 bet 並驗證 ack")
        code = await run_ws_step_async(
            ws=ws,
            event_name="bet",
            handler_func=handle_bet_ack,
            send_func=send_bet_async,
            timeout_sec=5,
            step_label="send_bet",
            account=account,
            game_name=game_name,
            step_success_records=step_success_records,
            error_records=error_records,
            ignore_error_codes=[ResultCode.TASK_BET_MISMATCHED]
        )
        log_step_result(code, step="send_bet", account=account, game_name=game_name)
        if code != ResultCode.SUCCESS:
            return code

        # Step 6: 發送 cur_round_finished 並驗證 ack
        print_info("🟢 Step 6: 發送 cur_round_finished 並驗證 ack")
        code = await run_ws_step_async(
            ws=ws,
            event_name="cur_round_finished",
            handler_func=handle_round_finished_ack,
            send_func=send_round_finished_async,
            timeout_sec=5,
            step_label="cur_round_finished",
            account=account,
            game_name=game_name,
            step_success_records=step_success_records,
            error_records=error_records,
        )
        log_step_result(code, step="cur_round_finished", account=account, game_name=game_name)
        if code != ResultCode.SUCCESS:
            return code

        # Step 7: 發送 exit_room 並驗證 ack
        print_info("🟢 Step 7: 發送 exit_room 並驗證 ack")
        code = await run_ws_step_async(
            ws=ws,
            event_name="exit_room",
            handler_func=handle_exit_room_ack,
            send_func=send_exit_room_async,
            timeout_sec=5,
            step_label="exit_room",
            account=account,
            game_name=game_name,
            step_success_records=step_success_records,
            error_records=error_records,
        )
        log_step_result(code, step="exit_room", account=account, game_name=game_name)
        if code != ResultCode.SUCCESS:
            return code

        print_info(f"[Step 7 ✅] exit_room 完成")
        return ResultCode.SUCCESS

    except Exception:
        code = ResultCode.TASK_EXCEPTION
        log_step_result(code, step="exception", account=account, game_name=game_name)
        return code
    finally:
        if ws:
            await close_ws_connection(ws)



from collections import defaultdict


def ws_connection_flow(task_list: List[dict], max_concurrency: int = 1) -> list:
    """
    子控制器流程：建立多條 WebSocket 並行連線，進行 join_room 驗證。
    最終統一印出錯誤摘要與「失敗任務中各步驟成功統計」與「錯誤碼清單」。
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

        # ✅ 額外列出錯誤碼清單
        non_success_codes = sorted(set(r for r in results if r != ResultCode.SUCCESS))
        if non_success_codes:
            print_info("❌ type_2 子控有錯誤發生")
            print_info(f"❌ 任務 001+009 執行失敗，錯誤碼：{non_success_codes}")

        return [r for r in results if r != ResultCode.SUCCESS]

    return asyncio.run(async_flow())