"""
工具模組：WebSocket async 事件分派器（只做轉發，不干涉流程）
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
    """
    將封包轉交給對應事件 handler，不處理錯誤碼與控制流程。
    """
    try:
        packet = json.loads(raw_data)
        event = packet.get("event")
        handler = _event_handlers.get(event)

        print(f"\n🧪 [dispatcher] 收到封包 event={event}")
        print(json.dumps(packet, indent=2, ensure_ascii=False))
        print(f"✅ handler 來源: {handler.__name__ if handler else '無'}")
        if handler:
            await handler(ws_obj, packet)
        else:
            print(f"⚠️  無對應事件 handler: {event}")
            # 不設錯誤碼，也不 set callback_done
            # 任務模組自己負責處理這種情況

        return ResultCode.SUCCESS

    except Exception as e:
        print(f"❌ [dispatcher] 封包解析失敗：{e}")
        # 不處理 callback_done，不設錯誤碼
        return ResultCode.TOOL_WS_DISPATCH_FAILED
