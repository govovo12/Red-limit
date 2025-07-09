# workspace/tools/ws/ws_connection_async_helper.py


import json

from workspace.tools.common.result_code import ResultCode
from workspace.tools.ws.ws_event_dispatcher_async import dispatch_event

import asyncio
import websockets

print(f"🧪 event loop before = {type(asyncio.get_event_loop())}")

if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print(f"🧪 event loop after  = {type(asyncio.get_event_loop())}")

async def open_ws_connection(ws_url: str, origin: str):
    """
    建立 WebSocket 連線（含 DEBUG 印出與相容處理）

    Returns:
        ws: WebSocket client 物件，或錯誤碼
    """
    try:
        print(f"🧪 websockets.connect 來源 = {websockets.connect}")
        print(f"🧪 websockets 版本 = {websockets.__version__}")
        headers = [("Origin", origin)]
        print("🧪 正在使用 tuple header 格式！")  # DEBUG 印出，確認你跑的是新版本
        ws = await websockets.connect(ws_url, extra_headers=headers)
        return ws
    except Exception as e:
        print(f"[EXCEPTION] WebSocket 建立失敗: {type(e)} | {e}")
        print(f"[DEBUG] URL = {ws_url}")
        print(f"[DEBUG] Origin = {origin}")
        return ResultCode.TOOL_WS_CONNECT_FAILED


async def start_ws_async(ws, callback=None) -> int:
    try:
        async for message in ws:
            try:
                await dispatch_event(message, ws)
            except json.JSONDecodeError:
                ws.error_code = ResultCode.TOOL_WS_INVALID_JSON
                return ResultCode.TOOL_WS_INVALID_JSON
            except Exception:
                ws.error_code = ResultCode.TOOL_WS_DISPATCH_FAILED
                return ResultCode.TOOL_WS_DISPATCH_FAILED

        return ResultCode.SUCCESS

    except asyncio.TimeoutError:
        ws.error_code = ResultCode.TOOL_WS_RECV_TIMEOUT
        return ResultCode.TOOL_WS_RECV_TIMEOUT
    except Exception:
        ws.error_code = ResultCode.TOOL_WS_RECV_LOOP_ERROR
        return ResultCode.TOOL_WS_RECV_LOOP_ERROR


async def close_ws_connection(ws) -> int:
    try:
        if ws and ws.connected:
            await ws.close()
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TOOL_WS_CLOSE_FAILED
