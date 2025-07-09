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
    """
    callback_event = asyncio.Event()
    ws_obj.callback_done = callback_event
    ws_obj.error_code = None  # 預設為 None，如果任務沒設，視為錯誤
    ws_obj.last_data = None

   

    # 發送封包
    await ws_obj.send(request_data)

    try:
        # 等待 callback
        await asyncio.wait_for(callback_event.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        error_records.append({
            "code": ResultCode.TOOL_WS_TIMEOUT,
            "step": step_name,
        })
        return ResultCode.TOOL_WS_TIMEOUT

    # 自訂 validator 驗證失敗
    if validator and not validator(ws_obj.last_data):
        error_records.append({
            "code": ResultCode.TOOL_WS_INVALID_DATA,
            "step": step_name,
        })
        return ResultCode.TOOL_WS_INVALID_DATA

    # 任務模組未設定 error_code，視為錯誤
    if ws_obj.error_code is None:
        error_records.append({
            "code": ResultCode.TASK_CALLBACK_NOT_SET,
            "step": step_name,
        })
        return ResultCode.TASK_CALLBACK_NOT_SET

    # 任務模組設定為失敗
    if ws_obj.error_code != ResultCode.SUCCESS:
        error_records.append({
            "code": ws_obj.error_code,
            "step": step_name,
        })
        return ws_obj.error_code

    # 成功記錄
    step_success_records.append({
        "step": step_name,
    })
    return ResultCode.SUCCESS


def _internal_callback(ws, data):
    """
    預設封包 callback handler：只儲存封包資料，不干涉流程。
    任務模組需自行設置 ws.error_code 與 callback_done.set()
    """
    ws.last_data = data

