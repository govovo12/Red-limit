from typing import Callable
from workspace.tools.ws.ws_fallback_handler import handle_unexpected_event  # 新增這行

_ws_event_handlers: dict[object, dict[str, Callable]] = {}


def register_event_handler(ws: object, event_name: str, handler: Callable) -> None:
    if ws not in _ws_event_handlers:
        _ws_event_handlers[ws] = {}
    _ws_event_handlers[ws][event_name] = handler
    

def unregister_event_handler(ws: object, event_name: str) -> None:
    if ws in _ws_event_handlers and event_name in _ws_event_handlers[ws]:
        del _ws_event_handlers[ws][event_name]


def clear_handlers(ws: object) -> None:
    if ws in _ws_event_handlers:
        del _ws_event_handlers[ws]


async def dispatch_event(ws: object, message: dict) -> None:
    """
    根據 event 分派封包到註冊的 handler，
    若找不到 handler，改由 fallback 處理。
    """
    event_name = message.get("event")
    if not event_name:
        return

    handlers = _ws_event_handlers.get(ws, {})

    if event_name in handlers:
        await handlers[event_name](ws, message)
    else:
        await handle_unexpected_event(ws, message)
    

# ✅ 可選：清空所有註冊表（debug 用）
def clear_all_event_handlers():
    _ws_event_handlers.clear()
