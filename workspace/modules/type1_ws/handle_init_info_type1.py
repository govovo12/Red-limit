"""
處理 type_1 的 init_info 封包任務模組
"""

from workspace.tools.common.result_code import ResultCode
from workspace.tools.ws.ws_callback_helper import callback_done

DEBUG = False  # 可改為 os.getenv("DEBUG_WS_PACKET", "false").lower() == "true"

async def handle_init_info(ws, message: dict):
    """
    專處理 event = 'init_info' 的封包，其他封包將略過。
    """
    try:
        if not isinstance(message, dict) or message.get("event") != "init_info":
            return  # 非目標封包略過

        if DEBUG:
            from workspace.tools.printer.printer import print_info
            print_info(f"[DEBUG] 收到 type_1 init_info 封包：\\n{message}")

        ws.rs_data = message
        ws.error_code = ResultCode.SUCCESS

    except Exception:
        ws.error_code = ResultCode.TASK_EXCEPTION

    callback_done(ws)
