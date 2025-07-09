import asyncio
from workspace.tools.ws.ws_connection_async_helper import open_ws_connection
from workspace.tools.common.result_code import ResultCode


async def open_ws_connection_task(ws_url: str, origin: str):
    """
    呼叫工具模組建立 WebSocket 連線，並補上子控需要的欄位。

    Returns:
        (code, ws): 若成功，回傳 (SUCCESS, ws)，否則回傳 (錯誤碼, None)
    """
    code, ws_or_msg = await open_ws_connection(ws_url, origin)
    if code != ResultCode.SUCCESS:
        return code, None

    ws = ws_or_msg

    # ✅ 子控流程需要這些欄位協助流程控制
    oid = ws_url.split("oid=")[-1]
    ws.oid = oid
    ws.callback_done = asyncio.Event()
    ws.error_code = ResultCode.SUCCESS

    return ResultCode.SUCCESS, ws
