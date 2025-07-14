from workspace.tools.common.result_code import ResultCode
import os

DEBUG = os.getenv("DEBUG_WS_PACKET", "false").lower() == "true"

async def handle_init_info(ws, message: dict):
    """
    專處理 event == 'init_info' 的封包，其它封包將略過。
    """
    try:
        if not isinstance(message, dict) or message.get("event") != "init_info":
            # 避免其他非預期封包誤觸
            return

        ws.rs_data = message
        if DEBUG:
            from workspace.tools.printer.printer import print_info
            print_info(f"[DEBUG] 收到 init_info 封包：\n{message}")
        ws.error_code = ResultCode.SUCCESS
        ws.callback_done.set()
    except Exception:
        ws.error_code = ResultCode.TASK_EXCEPTION
        ws.callback_done.set()
