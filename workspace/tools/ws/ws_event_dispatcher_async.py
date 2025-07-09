"""
工具模組：WebSocket async 事件分派器（含 debug 印出）

提供事件註冊與封包分派的功能，用於異步 WebSocket 回應解析。
"""

# === 錯誤碼與模組 ===
from workspace.tools.common.result_code import ResultCode

# === 標準工具 ===
import json
from typing import Callable, Any


_event_handlers: dict[str, Callable] = {}


def register_event_handler(event_name: str, handler_func: Callable) -> None:
    """
    註冊事件名稱對應的 async handler 函式
    """
    _event_handlers[event_name] = handler_func


async def dispatch_event(raw_data: str, ws_obj: Any) -> int:
    try:
        packet = json.loads(raw_data)
        event = packet.get("event")
        handler = _event_handlers.get(event)

        print(f"\n🧪 [dispatcher] 收到封包 event={event}")
        print(json.dumps(packet, indent=2, ensure_ascii=False))

        if handler:
            await handler(ws_obj, packet)
        else:
            print(f"⚠️  無對應事件 handler: {event}")
            ws_obj.error_code = ResultCode.TOOL_WS_EVENT_MISMATCH
            ws_obj.callback_done.set()  # 設置這個來避免死等

        if event == "join_room":
            # 僅在 join_room 時設置 _join_event
            if hasattr(ws_obj, "_join_event"):
                ws_obj._join_event.set()

        return ResultCode.SUCCESS

    except Exception as e:
        print(f"❌ [dispatcher] 封包解析失敗：{e}")
        if hasattr(ws_obj, "callback_done"):
            ws_obj.callback_done.set()

        ws_obj.error_code = ResultCode.TOOL_WS_DISPATCH_FAILED
        return ResultCode.TOOL_WS_DISPATCH_FAILED


