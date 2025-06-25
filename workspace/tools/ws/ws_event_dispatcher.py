import json
from websocket import WebSocketApp
from typing import Callable
from workspace.tools.printer.color_helper import cyan, green

def dispatch_event(ws: WebSocketApp, message: str) -> None:
    """
    根據封包中的 event 欄位，自動呼叫對應 handler，並印出 debug log。
    """
    try:
        data = json.loads(message)
        event = data.get("event")

        if not event:
            print("[dispatcher] ⚠️ 封包缺少 event 欄位，忽略。")
            return

        print(f"[dispatcher] 📩 收到封包 event：{event}")
        if hasattr(ws, "_event_handlers"):
            handler = ws._event_handlers.get(event)
            print(f"[dispatcher] 🔍 封包 event='{cyan(event)}' → 呼叫 {green(handler.__name__)}()")
            if handler:
                handler(ws, message)
            else:
                print(f"[dispatcher] ⚠️ 未找到 event「{event}」對應的 handler")
        else:
            print("[dispatcher] ⚠️ 此 ws 尚未註冊任何事件處理器")

    except Exception as e:
        print(f"[dispatcher] ❗ 解析封包失敗：{e}")
        # 不 raise，避免整條連線中斷


def register_event_handler(ws: WebSocketApp, event: str, handler: Callable[[WebSocketApp, str], None]) -> None:
    """
    登記事件處理器。不會自動綁定 dispatcher，需由外部自行決定是否要使用。
    """
    if not hasattr(ws, "_event_handlers"):
        ws._event_handlers = {}

    ws._event_handlers[event] = handler


def bind_dispatcher(ws: WebSocketApp) -> None:
    """
    明確綁定 dispatcher 為 ws.on_message，支援事件自動分派。
    """
    print(f"[dispatcher] ✅ 綁定 dispatcher 至 ws.on_message")
    ws.on_message = dispatch_event
