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

# 工具模組
from workspace.tools.ws.ws_connection_helper import start_ws, disconnect_ws
from workspace.tools.ws.ws_event_dispatcher import bind_dispatcher, register_event_handler

# 通用工具
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info, print_error


def ws_connection_flow(task_list: List[Dict], max_concurrency: int = 1) -> List[int]:
    """
    子控制器：執行 WebSocket 任務流程
    join_room → keep_alive → send_bet → cur_round_finished → exit_room
    """
    print_info(f"🚀 子控啟動：002 ws_connection_flow，總任務數：{len(task_list)}，最大併發：{max_concurrency}")
    results = []

    def handle_single_task(task: Dict) -> int:
        account = task.get("account")
        oid = task.get("oid")
        token = task.get("access_token")

        if not account or not oid or not token:
            print_error("❌ 任務缺少 account、oid 或 token")
            return ResultCode.INVALID_TASK

        print_info(f"📍 處理任務：account={account}, oid={oid}")
        ws_url = f"{R88_GAME_WS_BASE_URL}?token={token}&oid={oid}"

        # Step 1: 建立連線
        code, ws = open_ws_connection_task(ws_url=ws_url, origin=R88_GAME_WS_ORIGIN)
        if code != ResultCode.SUCCESS:
            print_error("❌ WebSocket 初始化失敗")
            return code

        # Step 2: join_room
        bind_dispatcher(ws)
        join_done = threading.Event()
        ws.callback_done = join_done
        register_event_handler(ws, "join_room", handle_join_room)

        start_ws(ws)
        join_done.wait(timeout=5)
        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code != ResultCode.SUCCESS:
            print_error(f"❌ join_room 失敗：oid={oid}，錯誤碼={error_code}")
            disconnect_ws(ws)
            return error_code
        print_info(f"✅ join_room 成功：oid={oid}")

        time.sleep(0.3)  # 延遲以確保伺服器建立遊戲房完成

        # Step 3: keep_alive
        hb_done = threading.Event()
        ws.callback_done = hb_done
        register_event_handler(ws, "keep_alive", handle_heartbeat_response)

        code = send_heartbeat(ws)
        if code != ResultCode.SUCCESS:
            print_error(f"❌ 發送 keep_alive 封包失敗：oid={oid}")
            disconnect_ws(ws)
            return code

        hb_done.wait(timeout=5)
        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code == ResultCode.SUCCESS:
            print_info(f"✅ keep_alive 成功：oid={oid}")
        else:
            print_error(f"❌ keep_alive 失敗：oid={oid}，錯誤碼={error_code}")
            disconnect_ws(ws)
            return error_code

        time.sleep(0.2)  # 延遲以確保伺服器驗證 keep_alive 後穩定

        # Step 4: send_bet
        bet_done = threading.Event()
        ws.callback_done = bet_done
        register_event_handler(ws, "bet", handle_bet_ack)

        code = send_bet_task(ws)
        if code != ResultCode.SUCCESS:
            print_error(f"❌ 發送下注封包失敗：oid={oid}，錯誤碼={code}")
            disconnect_ws(ws)
            return code

        bet_done.wait(timeout=5)
        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code == ResultCode.SUCCESS:
            print_info(f"✅ bet_ack 驗證通過：oid={oid}")
        else:
            print_error(f"❌ bet_ack 驗證失敗：oid={oid}，錯誤碼={error_code}")
            disconnect_ws(ws)
            return error_code

        time.sleep(0.4)  # 延遲以確保伺服器完成結算，避免 round_finish 送太早

        # Step 5: cur_round_finished
        rf_done = threading.Event()
        ws.callback_done = rf_done
        register_event_handler(ws, "cur_round_finished", handle_round_finished_ack)

        code = send_round_finished(ws)
        if code != ResultCode.SUCCESS:
            print_error(f"❌ 發送 cur_round_finished 封包失敗：oid={oid}")
            disconnect_ws(ws)
            return code

        rf_done.wait(timeout=5)
        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code == ResultCode.SUCCESS:
            print_info(f"✅ cur_round_finished 成功：oid={oid}")
        else:
            print_error(f"❌ cur_round_finished 失敗：oid={oid}，錯誤碼={error_code}")
            disconnect_ws(ws)
            return error_code

        time.sleep(0.3)  # 延遲以確保伺服器完全完成回合後再離房

        # Step 6: exit_room
        exit_done = threading.Event()
        ws.callback_done = exit_done
        register_event_handler(ws, "exit_room", handle_exit_room_ack)

        code = send_exit_room(ws)
        if code != ResultCode.SUCCESS:
            print_error(f"❌ 發送 exit_room 封包失敗：oid={oid}")
            disconnect_ws(ws)
            return code

        exit_done.wait(timeout=5)
        error_code = getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)
        if error_code == ResultCode.SUCCESS:
            print_info(f"✅ exit_room 成功：oid={oid}")
        else:
            print_error(f"❌ exit_room 失敗：oid={oid}，錯誤碼={error_code}")
            disconnect_ws(ws)
            return error_code

        # ✅ 全流程完成
        disconnect_ws(ws)
        return ResultCode.SUCCESS

    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        results = list(executor.map(handle_single_task, task_list))
    # ✅ 統計成功 / 失敗
    success_count = sum(1 for code in results if code == ResultCode.SUCCESS)
    fail_count = len(results) - success_count
    print_info(f"📊 子控執行統計：成功 {success_count} 筆，失敗 {fail_count} 筆")
    return results
