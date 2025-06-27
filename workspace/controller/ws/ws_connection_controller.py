import threading
import time
from typing import Dict

# 📦 快取與檔案資料載入工具
from workspace.tools.token.token_login_cache import load_login_token
from workspace.tools.file.data_loader import load_json
from workspace.config.paths import get_oid_list_path

# 🌐 WebSocket 連線參數與控制
from workspace.tools.env.config_loader import R88_GAME_WS_BASE_URL, R88_GAME_WS_ORIGIN
from workspace.modules.ws.open_ws_connection_task import open_ws_connection_task
from workspace.tools.ws.ws_connection_helper import disconnect_ws

# 🧩 任務模組 - 處理 join_room 封包
from workspace.modules.ws.handle_join_room import handle_join_room

# 🔀 Dispatcher 工具：綁定與註冊 handler
from workspace.tools.ws.ws_event_dispatcher import bind_dispatcher, register_event_handler

# ⚙️ 系統通用工具：錯誤碼、列印
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info, print_error

# 🧩 心跳相關工具
from workspace.modules.ws.send_heartbeat_task import send_heartbeat, handle_heartbeat_response

def ws_connection_flow(task: Dict) -> int:
    """
    子控制器：接收單一任務 dict，執行 WebSocket 流程（開連線 + join_room + 心跳）
    """
    # 從 task 中提取必要資料
    oid = task.get("oid")
    token = task.get("access_token")
    
    if not oid or not token:
        print_error("❌ 缺少必要的資料：oid 或 access_token")
        return ResultCode.TASK_MISSING_REQUIRED_DATA

    ws_url = f"{R88_GAME_WS_BASE_URL}?token={token}&oid={oid}"
    print_info(f"🚀 正在建立連線：oid={oid}")

    # Step 1: 開連線
    join_done = threading.Event()
    code, ws = open_ws_connection_task(ws_url=ws_url, origin=R88_GAME_WS_ORIGIN, done=join_done)
    if code != ResultCode.SUCCESS:
        print_error(f"❌ 開連線失敗：錯誤碼={code}")
        return code

    ws.oid = oid
    ws.task_data = task
    bind_dispatcher(ws)

    # Step 2: 處理 join_room 事件
    ws.callback_done = join_done
    register_event_handler(ws, "join_room", handle_join_room)
    join_done.wait(timeout=5)
    
    if getattr(ws, "error_code", 0) != ResultCode.SUCCESS:
        print_error(f"⚠️ join_room 回應異常：oid={oid}，錯誤碼={ws.error_code}")

    # Step 3: 等待兩秒，確保 join_room 完成後再發送心跳包
    time.sleep(2)

    # Step 4: 發送心跳包（keep_alive）
    heartbeat_done = threading.Event()
    ws.callback_done = heartbeat_done
    register_event_handler(ws, "keep_alive", handle_heartbeat_response)
    send_heartbeat(ws)  # 不再需要傳遞 task 參數
    heartbeat_done.wait(timeout=5)
    
    if getattr(ws, "error_code", 0) != ResultCode.SUCCESS:
        print_error(f"⚠️ keep_alive 回應異常：oid={oid}，錯誤碼={ws.error_code}")

    # Step 5: 關閉 WebSocket 連線
    disconnect_ws(ws)
    return getattr(ws, "error_code", ResultCode.SUCCESS)