import json
import asyncio
from typing import Callable, List, Optional, Dict, Any
from workspace.tools.common.result_code import ResultCode


import json
import asyncio
from typing import Callable, Optional, Any
from workspace.tools.common.result_code import ResultCode


async def run_ws_step_func_async(
    ws_obj: Any,
    step_func: Callable[[Any], Any],
    timeout: float = 8.0,
) -> int:
    """
    呼叫實際的 ws 任務函式（例如 send_heartbeat_async），並等待 callback_done。
    """
    if not hasattr(ws_obj, "callback_done") or ws_obj.callback_done is None:
        raise RuntimeError("❌ ws.callback_done 尚未初始化")

    if not hasattr(ws_obj, "error_code"):
        ws_obj.error_code = None
        ws_obj.last_data = None

    try:
        await step_func(ws_obj)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResultCode.TASK_SEND_HEARTBEAT_FAILED

    try:
        await asyncio.wait_for(ws_obj.callback_done.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        return ResultCode.TOOL_WS_TIMEOUT

    if ws_obj.error_code is None:
        return ResultCode.TOOL_WS_CALLBACK_NOT_SET

    return ws_obj.error_code






def _internal_callback(ws, data):
    """
    預設封包 callback handler：只儲存封包資料，不干涉流程。
    任務模組需自行設置 ws.error_code 與 callback_done.set()
    """
    ws.last_data = data

async def run_ws_send_and_wait_async(ws, send_func, payload: dict = None, timeout: int = 5) -> int:
    """
    發送封包並等待伺服器回應，適用於需要驗證 response 的封包（如 bet）

    Args:
        ws: WebSocket 物件
        send_func: 發送封包的函式，需支援 (ws) 或 (ws, payload)
        payload (dict, optional): 傳入封包的參數資料
        timeout (int): 等待封包處理完成的最大時間（秒）

    Returns:
        int: 任務模組設置的錯誤碼，或超時/發送錯誤
    """
    ws.callback_done = asyncio.Event()
    ws.error_code = ResultCode.TASK_EXCEPTION

    try:
        if payload is not None:
            await send_func(ws, payload)
        else:
            await send_func(ws)
    except Exception:
        return ResultCode.TOOL_WS_SEND_FAILED

    try:
        await asyncio.wait_for(ws.callback_done.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        return ResultCode.TOOL_WS_RESPONSE_TIMEOUT 

    return ws.error_code