# workspace/tools/printer/debug_helper.py

import os
from dotenv import load_dotenv

load_dotenv()
_DEBUG_FLAG = os.getenv("DEBUG_WS_PACKET", "false").lower() == "true"


def debug_print(message: str):
    """
    印出一般 debug 訊息（需開啟 DEBUG_WS_PACKET）
    """
    if _DEBUG_FLAG:
        print(f"[DEBUG] {message}")


def debug_traceback():
    """
    印出 traceback 訊息（需開啟 DEBUG_WS_PACKET）
    """
    if _DEBUG_FLAG:
        import traceback
        traceback.print_exc()


def debug_enabled() -> bool:
    """
    回傳目前是否啟用 debug 模式
    """
    return _DEBUG_FLAG
