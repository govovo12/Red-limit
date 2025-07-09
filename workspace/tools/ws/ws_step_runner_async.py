"""
工具模組：通用 WebSocket 步驟封裝器（支援 async）

註冊 handler → 發送封包 → 等待 callback → 分類成功與錯誤。
"""

# === 錯誤碼與模組 ===
from workspace.tools.ws.ws_event_dispatcher_async import register_event_handler
from workspace.tools.common.result_code import ResultCode

# === 標準工具 ===
import asyncio
from typing import Callable, List, Optional, Dict, Any


async def run_ws_step_async(
    ws_obj: Any,
    step_name: str,
    event_name: str,
    request_data: dict,
    step_success_records: List[Dict],
    error_records: List[Dict],
    validator: Optional[Callable[[dict], bool]] = None,
    timeout: float = 8.0,
) -> int:
    """
    發送封包並等待 callback 成功，記錄結果。

    Args:
        ws_obj (Any): WebSocket 對象（會被綁定 callback_done）
        step_name (str): 步驟名稱，用於紀錄與錯誤辨識
        event_name (str): 事件名稱，用於註冊與封包分派
        request_data (dict): 封包資料（會轉成 JSON 傳送）
        step_success_records (List[Dict]): 成功紀錄列表（會 append）
        error_records (List[Dict]): 錯誤紀錄列表（會 append）
        validator (Callable): 驗證回應資料是否符合期待，失敗視為錯誤
        timeout (float): 等待 callback 超時秒數

    Returns:
        int: 錯誤碼（成功為 0）
    """
    callback_event = asyncio.Event()
    ws_obj.callback_done = callback_event
    ws_obj.error_code = ResultCode.SUCCESS

    register_event_handler(event_name, lambda ws, data: _internal_callback(ws, data))

    await ws_obj.send(request_data)

    try:
        await asyncio.wait_for(callback_event.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        error_records.append({
            "code": ResultCode.TOOL_WS_TIMEOUT,
            "step": step_name,
        })
        return ResultCode.TOOL_WS_TIMEOUT

    if validator and not validator(ws_obj.last_data):
        error_records.append({
            "code": ResultCode.TOOL_WS_INVALID_DATA,
            "step": step_name,
        })
        return ResultCode.TOOL_WS_INVALID_DATA

    if ws_obj.error_code != ResultCode.SUCCESS:
        error_records.append({
            "code": ws_obj.error_code,
            "step": step_name,
        })
        return ws_obj.error_code

    step_success_records.append({
        "step": step_name,
    })
    return ResultCode.SUCCESS


def _internal_callback(ws, data):
    """
    預設封包 callback handler：儲存回應並結束等待。
    """
    ws.last_data = data
    if hasattr(ws, "callback_done"):
        ws.callback_done.set()
