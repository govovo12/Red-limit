import json
import asyncio

from websockets.legacy.client import connect as legacy_connect

from workspace.tools.common.result_code import ResultCode
from workspace.tools.ws.ws_event_dispatcher_async import dispatch_event


async def open_ws_connection(ws_url: str, origin: str) -> tuple:
    """
    建立 WebSocket 連線，回傳 (錯誤碼, ws 或錯誤訊息)
    """
    try:
        headers = [("Origin", origin)]
        ws = await legacy_connect(ws_url, extra_headers=headers)

        ws.error_code = ResultCode.SUCCESS
        ws.callback_done = None

        return ResultCode.SUCCESS, ws
    except Exception as e:
        return ResultCode.TOOL_WS_CONNECT_FAILED, str(e)


async def start_ws_async(ws, callback=None) -> int:
    """
    開始接收 WS 封包，並透過 dispatcher 處理事件。
    """
    try:
        async for message in ws:
            try:
                await dispatch_event(message, ws)
            except json.JSONDecodeError:
                # 忽略 JSON 格式錯誤，不中斷
                continue
            except Exception:
                continue
        return ResultCode.SUCCESS

    except asyncio.TimeoutError:
        ws.error_code = ResultCode.TOOL_WS_RECV_TIMEOUT
        return ResultCode.TOOL_WS_RECV_TIMEOUT

    except Exception:
        ws.error_code = ResultCode.TOOL_WS_RECV_LOOP_ERROR
        return ResultCode.TOOL_WS_RECV_LOOP_ERROR


async def close_ws_connection(ws) -> int:
    """
    關閉 WS 連線
    """
    try:
        if ws and ws.connected:
            await ws.close()
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TOOL_WS_CLOSE_FAILED
