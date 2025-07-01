# workspace/tools/ws/ws_event_dispatcher.py

import json
from websocket import WebSocketApp
import threading

# 儲存 event → handler 的映射表（使用 ws 實例隔離）
_event_handlers: dict[tuple[int, str], callable] = {}


def register_event_handler(ws: WebSocketApp, event_name: str, handler_func: callable) -> None:
    """
    註冊對應事件的封包處理函式（key 為 ws 實例 ID + event 名）
    """
    key = (id(ws), event_name)
    _event_handlers[key] = handler_func


def dispatch_event(ws: WebSocketApp, raw_data: str) -> None:
    """
    根據封包中的 event 分派到對應的 handler。
    注意：
    - 不處理錯誤碼設定
    - 不印出 log
    - 若 handler 發生例外仍保底釋放 callback_done
    """
    try:
        packet = json.loads(raw_data)
        event = packet.get("event")
        if not event:
            return  # 無 event 不處理

        key = (id(ws), event)
        handler = _event_handlers.get(key)
        if handler:
            handler(ws, packet)

    except Exception:
        # 任務模組未處理例外，仍保底釋放 callback_done 避免死等
        if hasattr(ws, "callback_done") and isinstance(ws.callback_done, threading.Event):
            ws.callback_done.set()


def bind_dispatcher(ws: WebSocketApp) -> None:
    """
    綁定 WebSocket 的 on_message 行為為 dispatch_event
    """
    ws.on_message = lambda ws, message: dispatch_event(ws, message)
