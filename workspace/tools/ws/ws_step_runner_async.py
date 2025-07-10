import json
import asyncio
from typing import Callable, List, Optional, Dict, Any
from workspace.tools.common.result_code import ResultCode


async def run_ws_step_async(
    ws_obj: Any,
    step_name: str,
    event_name: str,
    request_data: dict,
    step_success_records: List[Dict],
    error_records: List[Dict],
    ctx: Optional[Any] = None,
    validator: Optional[Callable[[dict], bool]] = None,
    timeout: float = 8.0,
) -> int:
    """
    發送封包並等待 callback 成功，記錄結果。
    """
    # ✅ 必須先由 controller 設定好 callback_done 事件鎖
    if not hasattr(ws_obj, "callback_done") or ws_obj.callback_done is None:
        raise RuntimeError("❌ ws.callback_done 尚未初始化，請在子控制器中設好 asyncio.Event()")

    if not hasattr(ws_obj, "error_code"):
        ws_obj.error_code = None
        ws_obj.last_data = None

    # ✅ 發送封包
    await ws_obj.send(json.dumps(request_data))

    try:
        await asyncio.wait_for(ws_obj.callback_done.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        error_records.append({
            "code": ResultCode.TOOL_WS_TIMEOUT,
            "step": step_name,
            "account": getattr(ctx, "account", None),
            "game_name": getattr(ctx, "game_name", None),
        })
        return ResultCode.TOOL_WS_TIMEOUT

    # ✅ 自訂驗證失敗
    if validator and not validator(ws_obj.last_data):
        error_records.append({
            "code": ResultCode.TOOL_WS_INVALID_DATA,
            "step": step_name,
            "account": getattr(ctx, "account", None),
            "game_name": getattr(ctx, "game_name", None),
        })
        return ResultCode.TOOL_WS_INVALID_DATA

    # ✅ handler 沒有設定 error_code，視為錯誤
    if ws_obj.error_code is None:
        error_records.append({
            "code": ResultCode.TOOL_WS_CALLBACK_NOT_SET,
            "step": step_name,
            "account": getattr(ctx, "account", None),
            "game_name": getattr(ctx, "game_name", None),
        })
        return ResultCode.TOOL_WS_CALLBACK_NOT_SET

    # ✅ handler 設了非成功錯誤碼
    if ws_obj.error_code != ResultCode.SUCCESS:
        error_records.append({
            "code": ws_obj.error_code,
            "step": step_name,
            "account": getattr(ctx, "account", None),
            "game_name": getattr(ctx, "game_name", None),
        })
        return ws_obj.error_code

    # ✅ 成功記錄
    step_success_records.append({
        "step": step_name,
        "account": getattr(ctx, "account", None),
        "game_name": getattr(ctx, "game_name", None),
    })
    return ResultCode.SUCCESS




def _internal_callback(ws, data):
    """
    預設封包 callback handler：只儲存封包資料，不干涉流程。
    任務模組需自行設置 ws.error_code 與 callback_done.set()
    """
    ws.last_data = data

