# workspace/tools/ws/ws_step_runner_async.py

from typing import Callable, List, Optional, Dict, Any
import asyncio

from workspace.tools.ws.ws_event_dispatcher_async import register_event_handler
from workspace.tools.common.result_code import ResultCode


async def run_ws_step_async(
    *,
    ws,
    event_name: str,
    handler_func: Callable,
    send_func: Callable,
    timeout_sec: int,
    step_label: str,
    account: str,
    game_name: str,
    step_success_records: List[Dict],
    error_records: List[Dict],
    ignore_error_codes: Optional[List[int]] = None,
    custom_validator: Optional[Callable[[Any], bool]] = None,
) -> int:
    """
    通用封裝：註冊 handler、發送封包、等待 callback、處理錯誤與記錄步驟。

    Parameters:
        ws: WebSocket 物件，需支援 .callback_done 與 .error_code
        event_name: 綁定的伺服器回應事件名
        handler_func: 處理伺服器回應封包的函式
        send_func: 用來發送封包的 async 函式
        timeout_sec: 等待伺服器回應的秒數
        step_label: 用於記錄與識別的步驟名稱
        account: 當前帳號名稱
        game_name: 遊戲名稱（供 log 用）
        step_success_records: 成功步驟記錄列表（會 append）
        error_records: 錯誤步驟記錄列表（會 append）
        ignore_error_codes: 可選，若 ws.error_code 為此列表中的錯誤碼，則視為 SUCCESS
        custom_validator: 可選，針對 ws 或其他條件額外驗證成功與否

    Returns:
        ResultCode.SUCCESS 或錯誤碼
    """
    ws.callback_done = asyncio.Event()
    register_event_handler(event_name, handler_func)

    code = await send_func(ws)
    if code != ResultCode.SUCCESS:
        error_records.append({
            "code": code,
            "step": f"{step_label}_send",
            "account": account,
            "game_name": game_name
        })
        return code

    try:
        await asyncio.wait_for(ws.callback_done.wait(), timeout=timeout_sec)
    except asyncio.TimeoutError:
        error_records.append({
            "code": ResultCode.TASK_WS_TIMEOUT,
            "step": f"{step_label}_timeout",
            "account": account,
            "game_name": game_name
        })
        return ResultCode.TASK_WS_TIMEOUT

    # 檢查 error_code 或自定驗證器
    if ws.error_code != ResultCode.SUCCESS:
        if ignore_error_codes and ws.error_code in ignore_error_codes:
            step_success_records.append({
                "step": f"{step_label} (ignored)",
                "account": account,
                "game_name": game_name
            })
            return ResultCode.SUCCESS
        error_records.append({
            "code": ws.error_code,
            "step": f"{step_label}_handler",
            "account": account,
            "game_name": game_name
        })
        return ws.error_code

    if custom_validator and not custom_validator(ws):
        error_records.append({
            "code": ResultCode.TASK_INVALID_DATA,
            "step": f"{step_label}_custom_check",
            "account": account,
            "game_name": game_name
        })
        return ResultCode.TASK_INVALID_DATA

    step_success_records.append({
        "step": step_label,
        "account": account,
        "game_name": game_name
    })
    return ResultCode.SUCCESS
