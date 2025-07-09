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
from workspace.tools.ws.ws_event_dispatcher_async import register_event_handler
from workspace.tools.ws.ws_step_runner_async import run_ws_step_async

# === 任務模組 ===
from workspace.modules.tpye2_ws.open_ws_connection_task import open_ws_connection_task
from workspace.modules.tpye2_ws.handle_join_room_async import handle_join_room_async
from workspace.modules.tpye2_ws.send_heartbeat_task import send_heartbeat_async, handle_heartbeat_response


async def handle_single_task_async(task, error_records, step_success_records):
    ws = None
    account = task.get("account")
    oid = task.get("oid")
    token = task.get("access_token")
    game_name = task.get("game_name")
    game_type = task.get("game_option_list_type")

    try:
        # Step 0: 準備參數
        print(f"[Step 0] 接收主控參數 account={account}, oid={oid}, game={game_name}")
        if not account or not oid or not token:
            code = ResultCode.INVALID_TASK
            log_step_result(code, step="prepare", account=account, game_name=game_name)
            return code

        # Step 1: 建立連線
        print("[Step 1] 建立 WebSocket 連線中...")
        ws_url = f"{get_ws_base_url_by_game_type(game_type)}?token={token}&oid={oid}"
        code, ws = await open_ws_connection_task(ws_url, R88_GAME_WS_ORIGIN)
        log_step_result(code, step="open_ws", account=account, game_name=game_name)
        if code != ResultCode.SUCCESS:
            return code
        step_success_records.append({"step": "open_ws", "account": account, "game_name": game_name})

        # Step 2: 註冊事件 handler
        print("[Step 2] 註冊事件處理器")
        ws._join_event = asyncio.Event()
        print(f"🧪 子控 ws id: {id(ws)}")
        register_event_handler("join_room", handle_join_room_async)
        register_event_handler("keep_alive", handle_heartbeat_response)

        # Step 3: 啟動接收 + 等待 join_room
        print("[Step 3] 啟動接收循環並等待 join_room 封包")
        asyncio.create_task(start_ws_async(ws))  # ✅ 不阻塞主流程
        try:
            await asyncio.wait_for(ws._join_event.wait(), timeout=10)
        except asyncio.TimeoutError:
            code = ResultCode.TASK_WS_TIMEOUT
            log_step_result(code, step="join_room_timeout", account=account, game_name=game_name)
            return code

        log_step_result(ws.error_code, step="join_room", account=account, game_name=game_name)
        if ws.error_code != ResultCode.SUCCESS:
            return ws.error_code
        step_success_records.append({"step": "join_room", "account": account, "game_name": game_name})

        # Step 4: 發送 keep_alive
        print("[Step 4] 發送 keep_alive 封包")
        code = await run_ws_step_async(
            ws_obj=ws,
            step_name="keep_alive",
            event_name="keep_alive",
            request_data={"event": "keep_alive"},
            step_success_records=step_success_records,
            error_records=error_records,
        )
        log_step_result(code, step="keep_alive", account=account, game_name=game_name)
        if code != ResultCode.SUCCESS:
            return code

        return ResultCode.SUCCESS

    except Exception:
        code = ResultCode.TASK_EXCEPTION
        log_step_result(code, step="exception", account=account, game_name=game_name)
        return code

    finally:
        if ws:
            await close_ws_connection(ws)


def ws_connection_flow(task_list, max_concurrency: int = 1):
    async def async_flow():
        error_records = []
        step_success_records = []

        tasks = [handle_single_task_async(t, error_records, step_success_records) for t in task_list]
        results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r == ResultCode.SUCCESS)
        print_info(f"[Flow ✅] 全部完成，共成功 {success} 筆，失敗 {len(error_records)} 筆")

        if error_records:
            print_error("❌ 子控失敗清單如下：")
            for err in error_records:
                label = "⚠ WARNING" if err["code"] == ResultCode.TASK_BET_MISMATCHED else "❌ ERROR"
                print_error(f"{label} code={err['code']} | step={err['step']} | account={err.get('account')} | game={err.get('game_name')}")

            # 額外列出錯誤帳號內成功步驟統計
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

        return [r for r in results if r != ResultCode.SUCCESS]

    return asyncio.run(async_flow())
