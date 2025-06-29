import json
import threading

from workspace.tools.env.config_loader import BET_LEVEL_MODE
from workspace.tools.common.result_code import ResultCode
from typing import Callable
from websocket import WebSocketApp

def handle_join_room(ws: WebSocketApp, message: str) -> None:
    """
    任務模組：處理 join_room 封包，解析 bet_info 並綁定下注上下文。
    強化除錯用，會印出封包與型別。
    """
    try:
        print("\n📨 [handler] join_room 被呼叫！")
        print(f"📨 [handler] message 型別 = {type(message)}, 長度 = {len(message) if message else 0}")
        print(f"📨 [handler] 原始封包內容 = {repr(message)}")

        packet = json.loads(message)
        event_type = packet.get("event")

        if event_type == "server_error":
            ws.error_code = ResultCode.TASK_JOIN_ROOM_SERVER_ERROR
            return

        if event_type != "join_room":
            return

        bet_info = packet.get("bet_info", {})
        if not bet_info or not isinstance(bet_info, dict):
            ws.error_code = ResultCode.TASK_BET_INFO_INCOMPLETE
            return

        ctx = {}
        for key, value in bet_info.items():
            if value is None:
                continue
            if isinstance(value, list) and value:
                ctx[key] = max(value) if (key == "bet_level" and BET_LEVEL_MODE == "max") else min(value)
            else:
                ctx[key] = value

        total_bet = 1
        for val in ctx.values():
            try:
                total_bet *= float(val)
            except (TypeError, ValueError):
                continue
        ctx["total_bet"] = total_bet

        if not ctx or total_bet == 0:
            ws.error_code = ResultCode.TASK_BET_INFO_INCOMPLETE
            return

        ws.bet_context = ctx
        ws.error_code = ResultCode.SUCCESS

    except Exception as e:
        print(f"❌ join_room 處理錯誤: {e}")
        ws.error_code = ResultCode.TASK_PACKET_PARSE_FAILED

    finally:
        if hasattr(ws, "callback_done") and isinstance(ws.callback_done, threading.Event):
            ws.callback_done.set()



def register_event_handler(ws: WebSocketApp, event: str, handler: Callable[[WebSocketApp, str], None]) -> None:
    """
    登記事件處理器，不會自動啟用 dispatcher，由外部自行決定是否要使用。
    """
    if not hasattr(ws, "_event_handlers"):
        ws._event_handlers = {}

    ws._event_handlers[event] = handler

def bind_dispatcher(ws: WebSocketApp) -> None:
    """
    綁定 dispatcher 為 ws.on_message 以支援事件自動分派。
    """
    print(f"[dispatcher] 🔗 綁定 dispatcher 至 ws.on_message")
    ws.on_message = dispatch_event

def dispatch_event(ws: WebSocketApp, message: str) -> None:
    """
    Dispatcher 主控：根據封包中的 event 欄位自動呼叫註冊的 handler。
    """
    try:
        print(f"[dispatcher] 📦 收到原始封包（前 100 字）: {repr(message[:100])}")

        data = json.loads(message)
        event = data.get("event")

        if not event:
            print("[dispatcher] ⚠️ 封包缺少 event 欄位，忽略")
            return

        print(f"[dispatcher] 📩 收到封包 event={event}")

        if hasattr(ws, "_event_handlers"):
            print(f"[dispatcher] 🧪 已註冊的 handlers：{list(ws._event_handlers.keys())}")
            handler = ws._event_handlers.get(event)
            if handler:
                print(f"[dispatcher] 🔄 執行 handler：{handler.__name__}() for event={event}")
                handler(ws, message)
            else:
                print(f"[dispatcher] ⚠️ 無對應 handler：event={event}")
        else:
            print("[dispatcher] ⚠️ 尚未綁定 handler 字典")

    except Exception as e:
        print(f"[dispatcher] ❌ dispatch_event 發生錯誤：{e}")
def dispatch_event(ws: WebSocketApp, message: str) -> None:
    try:
        # ✅ 封包觀察機制：自訂 log callback
        if hasattr(ws, "packet_logger") and callable(ws.packet_logger):
            try:
                data = json.loads(message)
                event = data.get("event", "unknown")
            except Exception:
                event = "invalid_json"
            ws.packet_logger(event, message)

        data = json.loads(message)
        event = data.get("event")

        if not event:
            print("[dispatcher] ⚠️ 封包缺少 event 欄位，忽略")
            return

        print(f"[dispatcher] 📩 收到封包 event={event}")

        if hasattr(ws, "_event_handlers"):
            handler = ws._event_handlers.get(event)
            if handler:
                print(f"[dispatcher] 🔄 執行 handler：{handler.__name__}() for event={event}")
                handler(ws, message)
            else:
                print(f"[dispatcher] ⚠️ 無對應 handler：event={event}")
        else:
            print("[dispatcher] ⚠️ 尚未綁定 handler 字典")

    except Exception as e:
        print(f"[dispatcher] ❌ dispatch_event 發生錯誤：{e}")
