import threading
import time
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

# 快取與環境設定
from workspace.tools.env.config_loader import R88_GAME_WS_BASE_URL, R88_GAME_WS_ORIGIN

# 任務模組
from workspace.modules.ws.open_ws_connection_task import open_ws_connection_task
from workspace.modules.ws.handle_join_room import handle_join_room
from workspace.modules.ws.send_heartbeat_task import send_heartbeat, handle_heartbeat_response
from workspace.modules.ws.send_bet_task import send_bet_task
from workspace.modules.ws.parse.parse_bet_response import handle_bet_ack
from workspace.modules.ws.send_round_finished import send_round_finished, handle_round_finished_ack
from workspace.modules.ws.send_exit_room import send_exit_room, handle_exit_room_ack
from workspace.modules.task.recharge_wallet_task import recharge_wallet

# 工具模組
from workspace.tools.ws.ws_connection_helper import start_ws, disconnect_ws
from workspace.tools.ws.ws_event_dispatcher import bind_dispatcher, register_event_handler

# 通用工具
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info
from workspace.tools.common.log_helper import log_simple_result


def ws_connection_flow(task_list: List[Dict], max_concurrency: int = 1) -> List[int]:
    """
    子控制器：執行 WebSocket 任務流程
    join_room → keep_alive → send_bet → cur_round_finished → exit_room
    """
    print_info(f"🚀 子控啟動：002 ws_connection_flow，任務數：{len(task_list)}，最大併發：{max_concurrency}")
    results = []

    def handle_single_task(task: Dict) -> int:
        # Step 0: 解析任務參數
        account = task.get("account")
        oid = task.get("oid")
        token = task.get("access_token")

        if not account or not oid or not token:
            log_simple_result(ResultCode.INVALID_TASK, "準備任務參數", oid=oid)
            return ResultCode.INVALID_TASK

        print_info(f"[Step 0] 📍 處理任務：account={account}, oid={oid}")

        # Step 0.5: 開始加值（recharge_wallet）
        print_info(f"[Step 0.5] 💰 開始加值：account={account}")
        recharge_code = recharge_wallet(account)
        if recharge_code != ResultCode.SUCCESS:
            log_simple_result(recharge_code, "recharge_wallet", oid=oid)
            return recharge_code


        # Step 0.6：組合 WebSocket URL
        print_info(f"[Step 0.6] 🧩 組合 ws_url：token={token} oid={oid}")
        ws_url = f"{R88_GAME_WS_BASE_URL}?token={token}&oid={oid}"
        print_info(f"🔗 ws_url: {ws_url}")

        # Step 1: 建立連線
        print_info(f"[Step 1] 🚪 建立 WebSocket 連線：oid={oid}")
        code, ws = open_ws_connection_task(ws_url=ws_url, origin=R88_GAME_WS_ORIGIN)
        if code != ResultCode.SUCCESS:
            log_simple_result(code, "open_ws", oid=oid)
            return code
        print_info(f"[Step 1 ✅] WebSocket 建立成功：oid={oid}")

        # Step 2: 註冊 join_room handler
        bind_dispatcher(ws)
        join_done = threading.Event()
        ws.callback_done = join_done
        register_event_handler(ws, "join_room", handle_join_room)
        print_info(f"[Step 2] 🧩 註冊 join_room handler：oid={oid}")

        # Step 3: 啟動連線
        start_ws(ws)
        print_info(f"[Step 3] 🚀 啟動 WebSocket 連線：oid={oid}")
        join_done.wait(timeout=5)

        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code != ResultCode.SUCCESS:
            log_simple_result(error_code, "join_room", oid=oid)
            disconnect_ws(ws)
            return error_code
        print_info(f"[Step 4] ✅ join_room 成功：oid={oid}")

        time.sleep(0.3)

        # Step 5: keep_alive
        print_info(f"[Step 5] 🚀 發送 keep_alive 封包：oid={oid}")
        hb_done = threading.Event()
        ws.callback_done = hb_done
        register_event_handler(ws, "keep_alive", handle_heartbeat_response)

        code = send_heartbeat(ws)
        if code != ResultCode.SUCCESS:
            log_simple_result(code, "keep_alive", oid=oid)
            disconnect_ws(ws)
            return code

        hb_done.wait(timeout=5)
        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code == ResultCode.SUCCESS:
            print_info(f"[Step 5-1] ✅ keep_alive 成功：oid={oid}")
        else:
            log_simple_result(error_code, "keep_alive", oid=oid)
            disconnect_ws(ws)
            return error_code

        time.sleep(0.2)

        # Step 6: send_bet
        print_info(f"[Step 6] 🚀 發送 bet 封包：oid={oid}")
        bet_done = threading.Event()
        ws.callback_done = bet_done
        register_event_handler(ws, "bet", handle_bet_ack)

        code = send_bet_task(ws)
        if code != ResultCode.SUCCESS:
            log_simple_result(code, context=f"send_bet / oid={oid}")
            disconnect_ws(ws)
            return code

        bet_done.wait(timeout=5)
        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code == ResultCode.SUCCESS:
            print_info(f"[Step 6-1] ✅ bet_ack 驗證成功：oid={oid}")
        else:
            log_simple_result(error_code, context=f"bet_ack / oid={oid}")
            disconnect_ws(ws)
            return error_code

        time.sleep(0.4)

        # Step 7: cur_round_finished
        print_info(f"[Step 7] 🎯 發送 cur_round_finished 封包：oid={oid}")
        rf_done = threading.Event()
        ws.callback_done = rf_done
        register_event_handler(ws, "cur_round_finished", handle_round_finished_ack)

        code = send_round_finished(ws)
        if code != ResultCode.SUCCESS:
            log_simple_result(code, "cur_round_finished", oid=oid)
            disconnect_ws(ws)
            return code

        rf_done.wait(timeout=5)
        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code == ResultCode.SUCCESS:
            print_info(f"[Step 7-1] ✅ cur_round_finished 成功：oid={oid}")
        else:
            log_simple_result(error_code, "cur_round_finished", oid=oid)
            disconnect_ws(ws)
            return error_code

        time.sleep(0.3)

        # Step 8: exit_room
        print_info(f"[Step 8] 🚪 發送 exit_room 封包：oid={oid}")
        exit_done = threading.Event()
        ws.callback_done = exit_done
        register_event_handler(ws, "exit_room", handle_exit_room_ack)

        code = send_exit_room(ws)
        if code != ResultCode.SUCCESS:
            log_simple_result(code, "exit_room", oid=oid)
            disconnect_ws(ws)
            return code

        exit_done.wait(timeout=5)
        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code == ResultCode.SUCCESS:
            print_info(f"[Step 8-1] ✅ exit_room 成功：oid={oid}")
        else:
            log_simple_result(error_code, "exit_room", oid=oid)
            disconnect_ws(ws)
            return error_code

        disconnect_ws(ws)
        return ResultCode.SUCCESS

    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        results = list(executor.map(handle_single_task, task_list))

    success_count = sum(1 for code in results if code == ResultCode.SUCCESS)
    fail_count = len(results) - success_count
    print_info(f"📊 子控執行統計：成功 {success_count} 筆，失敗 {fail_count} 筆")
    return results
