import json
import asyncio

from websockets.legacy.client import connect as legacy_connect

from workspace.tools.common.result_code import ResultCode
from workspace.tools.ws.ws_event_dispatcher_async import dispatch_event



async def open_ws_connection(ws_url: str, origin: str):
    """
    建立 WebSocket 連線（使用 legacy.client.connect 相容寫法）

    Returns:
        ws: WebSocket client 物件，或錯誤碼
    """
    try:
        headers = [("Origin", origin)]
        ws = await legacy_connect(ws_url, extra_headers=headers)

        # ✅ 初始化必要欄位（這裡也可以交由呼叫方補）
        ws.error_code = ResultCode.SUCCESS
        ws.callback_done = None

        return ws
    except Exception:
        return ResultCode.TOOL_WS_CONNECT_FAILED


async def start_ws_async(ws, callback=None) -> int:
    try:
        print(f"🧪 start_ws_async ws id: {id(ws)}")
        async for message in ws:
            try:
                await dispatch_event(message, ws)
            except json.JSONDecodeError:
                print("⚠️ JSON 格式錯誤，略過此封包")
                # 不中斷主流程
                continue
            except Exception as e:
                print(f"⚠️ 封包處理錯誤：{e}，略過此封包")
                continue

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
