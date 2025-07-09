"""
工具模組：WebSocket async 事件分派器

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

    Args:
        event_name (str): 封包中的 event 名稱
        handler_func (Callable): 可 await 的 async handler(ws, data)
    """
    _event_handlers[event_name] = handler_func


async def dispatch_event(raw_data: str, ws_obj: Any) -> int:
    """
    分派封包事件給已註冊的 handler，失敗回傳錯誤碼。

    Args:
        raw_data (str): WebSocket 傳回的封包 JSON 字串
        ws_obj (Any): 提供給 handler 使用的 WebSocket 對象（可含 callback_done, error_code）

    Returns:
        int: ResultCode（成功為 SUCCESS，否則錯誤碼）
    """
    try:
        packet = json.loads(raw_data)
        event = packet.get("event")
        handler = _event_handlers.get(event)

        if handler:
            await handler(ws_obj, packet)

        return ResultCode.SUCCESS

    except Exception:
        if hasattr(ws_obj, "callback_done"):
            ws_obj.callback_done.set()

        ws_obj.error_code = ResultCode.TOOL_WS_DISPATCH_FAILED
        return ResultCode.TOOL_WS_DISPATCH_FAILED
