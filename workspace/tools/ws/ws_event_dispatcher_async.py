"""
工具模組：WebSocket async 事件分派器

非同步架構下的 event-handler 映射表，用於手動解析封包時進行分派。
"""

_event_handlers: dict[str, callable] = {}


def register_event_handler(event_name: str, handler_func: callable) -> None:
    """
    註冊事件名稱對應的 async handler function
    """
    _event_handlers[event_name] = handler_func


async def dispatch_event(raw_data: str, ws_obj: any) -> None:
    """
    分派封包事件（需手動呼叫），支援 awaitable handler
    Args:
        raw_data (str): WebSocket 傳回的封包 JSON 字串
        ws_obj (any): 提供給 handler 使用的 ws 對象（可帶錯誤碼、callback_done）
    """
    try:
        import json
        packet = json.loads(raw_data)
        event = packet.get("event")

        handler = _event_handlers.get(event)
        if handler:
            await handler(ws_obj, packet)

    except Exception as e:
        print(f"[DISPATCH ERROR] {e}")
        if hasattr(ws_obj, "callback_done"):
            ws_obj.callback_done.set()
