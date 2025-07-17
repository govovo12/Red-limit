"""
處理 type_1 的 init_info 封包任務模組
"""

import os
from workspace.tools.common.result_code import ResultCode
from workspace.tools.ws.ws_callback_helper import callback_done
from workspace.tools.printer.printer import print_info
from dotenv import load_dotenv

# ✅ 自動載入 .env 設定（只做一次不會有副作用）
load_dotenv()

# ✅ 由 .env 中讀取 DEBUG_WS_PACKET（預設關閉）
DEBUG = os.getenv("DEBUG_WS_PACKET", "false").lower() == "true"


async def handle_init_info(ws, message: dict):
    """
    專處理 event = 'init_info' 的封包，其他封包將略過。
    """
    try:
        if not isinstance(message, dict) or message.get("event") != "init_info":
            return  # 非目標封包略過

        if DEBUG:
            print_info(f"[DEBUG] 📩 收到 type_1 init_info 封包 (ws id={id(ws)}):\n{message}")

        ws.rs_data = message
        ws.error_code = ResultCode.SUCCESS

    except Exception as e:
        ws.error_code = ResultCode.TASK_EXCEPTION
        if DEBUG:
            print_info(f"[DEBUG] ❌ 發生例外：{e}")

    callback_done(ws)
    if DEBUG:
        print_info(f"[DEBUG] ☑ callback_done 已 set (ws id={id(ws)})")
