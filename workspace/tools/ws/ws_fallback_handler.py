# workspace/tools/ws/ws_fallback_handler.py

import os
from workspace.tools.common.result_code import ResultCode
from workspace.tools.ws.ws_callback_helper import callback_done
from workspace.tools.printer.debug_helper import debug_print

# 開發模式下才印封包細節
DEBUG = os.getenv("DEBUG_WS_PACKET", "false").lower() == "true"

IGNORED_EVENTS = {
    "websocket",
    "matching",
    "ping",
    "pong",
    "server_timestamp",
}

ERROR_EVENTS = {
    "server_error",
    "kick_out",
    "login_fail",
}

async def handle_unexpected_event(ws, message: dict):
    event = message.get("event")

    if event in IGNORED_EVENTS:
        if DEBUG:
            debug_print(f"[略過] 收到合法但不需處理的封包 event={event}")
        return

    if event in ERROR_EVENTS:
        if DEBUG:
            debug_print(f"[錯誤] 收到未註冊但屬於錯誤封包 event={event}")
        ws.error_code = ResultCode.TOOL_WS_UNEXPECTED_EVENT
        callback_done(ws)
        return

    if DEBUG:
        debug_print(f"[忽略] 未知 event={event} msg={message}")
    # ❗ 不 callback，也不設錯誤碼

