import json
import asyncio
from typing import Callable, List, Optional, Dict, Any
from workspace.tools.common.result_code import ResultCode


import json
import asyncio
from typing import Callable, Optional, Any
from workspace.tools.common.result_code import ResultCode


async def run_ws_step_async(
    ws_obj: Any,
    event_name: str,
    request_data: dict,
    validator: Optional[Callable[[dict], bool]] = None,
    timeout: float = 8.0,
) -> int:
    """
    精簡版：只負責發送封包與等待 callback_done。
    - 不處理 ctx
    - 不記錄成功/錯誤記錄
    - 不干涉流程
    """
    # ✅ 前置檢查
    if not hasattr(ws_obj, "callback_done") or ws_obj.callback_done is None:
        raise RuntimeError("❌ ws.callback_done 尚未初始化")

    if not hasattr(ws_obj, "error_code"):
        ws_obj.error_code = None
        ws_obj.last_data = None

    # ✅ 發送封包
    await ws_obj.send(json.dumps(request_data))

    # ✅ 等待任務模組 callback
    try:
        await asyncio.wait_for(ws_obj.callback_done.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        return ResultCode.TOOL_WS_TIMEOUT

    # ✅ 驗證資料內容（可選）
    if validator and not validator(ws_obj.last_data):
        return ResultCode.TOOL_WS_INVALID_DATA

    # ✅ 沒有錯誤碼（callback 沒設）
    if ws_obj.error_code is None:
        return ResultCode.TOOL_WS_CALLBACK_NOT_SET

    # ✅ 回傳 handler 回傳的錯誤碼（或成功）
    return ws_obj.error_code





def _internal_callback(ws, data):
    """
    預設封包 callback handler：只儲存封包資料，不干涉流程。
    任務模組需自行設置 ws.error_code 與 callback_done.set()
    """
    ws.last_data = data

