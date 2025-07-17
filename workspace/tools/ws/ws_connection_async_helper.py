import json
import asyncio
from websockets.legacy.client import connect as legacy_connect

from workspace.tools.common.result_code import ResultCode
from workspace.tools.ws.ws_event_dispatcher_async import dispatch_event
from workspace.tools.printer.debug_helper import debug_print, debug_traceback


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
        debug_print(f"❌ WS 連線例外：{e}")
        debug_traceback()
        return ResultCode.TOOL_WS_CONNECT_FAILED, str(e)


async def start_ws_async(ws, callback=None) -> int:
    """
    開始接收 WS 封包，並透過 dispatcher 處理事件。
    """
    try:
        debug_print(f"[WS] ws id={id(ws)} 開始接收封包")

        async for message in ws:
            try:
                parsed = json.loads(message)
                await dispatch_event(ws, parsed)

            except json.JSONDecodeError as e:
                debug_print(f"❌ JSON 格式錯誤：{e}")
                continue

            except Exception as e:
                debug_print(f"❌ dispatch handler 發生錯誤：{e}")
                debug_traceback()
                continue

        return ResultCode.SUCCESS

    except Exception as e:
        debug_traceback()
        debug_print(f"❌ WebSocket 接收封包錯誤 (ws id={id(ws)}): {e}")

        ws.error_code = ResultCode.TOOL_WS_RECV_LOOP_ERROR

        if hasattr(ws, "callback_done") and ws.callback_done:
            ws.callback_done.set()

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
