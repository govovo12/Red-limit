from typing import Callable

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
    event_name = message.get("event")
    if not event_name:
        return

    if ws in _ws_event_handlers and event_name in _ws_event_handlers[ws]:
        await _ws_event_handlers[ws][event_name](ws, message)
    

# ✅ 可選：清空所有註冊表（debug 用）
def clear_all_event_handlers():
    _ws_event_handlers.clear()
