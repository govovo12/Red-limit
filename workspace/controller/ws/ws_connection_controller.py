import threading
from typing import Optional

# 📦 快取與檔案資料載入工具
from workspace.tools.token.token_login_cache import load_login_token
from workspace.tools.file.data_loader import load_json
from workspace.config.paths import get_oid_list_path

# 🌐 WebSocket 連線參數與控制
from workspace.tools.env.config_loader import R88_GAME_WS_BASE_URL, R88_GAME_WS_ORIGIN
from workspace.modules.ws.open_ws_connection_task import open_ws_connection_task
from workspace.tools.ws.ws_connection_helper import disconnect_ws

# 🔁 WebSocket 封包任務模組（send + callback handler）
from workspace.modules.ws.handle_join_room import handle_join_room
from workspace.modules.ws.send_heartbeat_task import send_heartbeat, handle_heartbeat_response
from workspace.modules.ws.send_bet_task import send_bet_task
from workspace.modules.ws.parse.parse_bet_response import handle_bet_ack      # ✅ 唯一在 parse 子資料夾
from workspace.modules.ws.send_round_finished import send_round_finished, handle_round_finished_ack
from workspace.modules.ws.send_exit_room import send_exit_room, handle_exit_room_ack

# 🔀 Dispatcher 工具：綁定與註冊 handler
from workspace.tools.ws.ws_event_dispatcher import bind_dispatcher, register_event_handler

# ⚙️ 系統通用工具：錯誤碼、列印、task 裝飾器
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.decorator import task



# workspace/controller/ws/ws_connection_controller.py

@task("002")
def ws_connection_flow(account: str = "qa0002", oid: Optional[str] = None) -> int:
    """
    子控制器：執行 WebSocket 初始化流程（開連線、處理 join_room、驗證下注金額）
    """
    print_info("📦 [2/2] 執行任務 002：驗證初始化封包...")
    print_info("🚀 執行子控制器：ws_connection_flow")

    # 允許不中斷流程的錯誤碼
    ALLOW_CONTINUE_ERROR_CODES = [
        ResultCode.TASK_BET_AMOUNT_RULE_VIOLATED,  # 10024
        ResultCode.TASK_BET_MISMATCHED,            # 10034
    ]
    # 1. 載入必要參數
    token = load_login_token(account)
    code, oid_list = load_json(get_oid_list_path())
    if code != ResultCode.SUCCESS:
        return code
    if not oid_list:
        print_error("❌ OID 清單為空")
        return ResultCode.TASK_SINGLE_WS_OID_LIST_EMPTY
    if oid is None:
        oid = str(oid_list[0])

    print_info(f"🎯 使用帳號 {account}，OID={oid}")

    # 2. 建立 WS 連線
    done = threading.Event()
    ws_url = f"{R88_GAME_WS_BASE_URL}?token={token}&oid={oid}"
    code, ws = open_ws_connection_task(ws_url=ws_url, origin=R88_GAME_WS_ORIGIN, done=done)
    if code != ResultCode.SUCCESS:
        return code
    ws.oid = oid

    # Dispatcher handler 註冊
    bind_dispatcher(ws)
    register_event_handler(ws, "join_room", handle_join_room)
    ws.callback_done = done
    done.wait(timeout=5)

    # 3. 心跳
    heartbeat_done = threading.Event()
    ws.callback_done = heartbeat_done
    register_event_handler(ws, "keep_alive", handle_heartbeat_response)
    send_heartbeat(ws)
    heartbeat_done.wait(timeout=3)

    # 4. 發送下注
    bet_done = threading.Event()
    ws.callback_done = bet_done
    register_event_handler(ws, "bet", handle_bet_ack)
    send_bet_task(ws)
    bet_done.wait(timeout=5)



    # 5. 發送 cur_round_finished
    round_done = threading.Event()
    ws.callback_done = round_done
    register_event_handler(ws, "cur_round_finished", handle_round_finished_ack)
    send_round_finished(ws)
    round_done.wait(timeout=5)

    # 6. 發送 exit_room
    exit_done = threading.Event()
    ws.callback_done = exit_done
    register_event_handler(ws, "exit_room", handle_exit_room_ack)
    send_exit_room(ws)
    exit_done.wait(timeout=5)

    # ✅ 暴露 ws 給測試或 fixture 使用（含 .bet_context, .bet_result）
    ws_connection_flow.last_ws = ws

    # 7. 關閉連線並回傳錯誤碼
    disconnect_ws(ws)
    # 8. ✅ 統一回傳錯誤碼，讓 pytest 斷言是否成功
    if getattr(ws, "error_code", 0) != ResultCode.SUCCESS:
        print_error(f"⚠️ 收到錯誤碼（不中斷流程）：{ws.error_code}")

    return getattr(ws, "error_code", ResultCode.TASK_CALLBACK_TIMEOUT)

