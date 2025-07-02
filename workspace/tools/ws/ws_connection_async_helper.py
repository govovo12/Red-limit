"""
工具模組：WebSocket 連線（async 版本）

此模組提供非同步方式建立與關閉 WebSocket 連線，使用 websockets 套件實作。
適用於 async 架構下的子控流程，可安全 await 控制 WS 壽命與異常處理。
"""

import asyncio
import websockets
from websockets.legacy.client import WebSocketClientProtocol
from workspace.tools.ws.ws_event_dispatcher_async import dispatch_event
from workspace.tools.common.result_code import ResultCode
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

async def open_ws_connection(ws_url: str, origin: str) -> WebSocketClientProtocol | None:
    """
    建立 WebSocket 連線（async 版本）

    Args:
        ws_url (str): 完整的 WebSocket 連線 URL
        origin (str): HTTP Origin 頭資訊

    Returns:
        WebSocketClientProtocol | None: 成功回傳 ws 連線物件，失敗回傳 None
    """
    try:
        ws = await websockets.connect(
            ws_url,
            origin=origin,
            ping_interval=30,   # 可視需求調整
            ping_timeout=10
        )
        print("[INFO] ✅ WS 連線成功")
        return ws

    except Exception as e:
        print(f"[ERROR] ❌ 建立 WS 連線失敗：{e}")
        return None


async def close_ws_connection(ws: WebSocketClientProtocol) -> None:
    """
    關閉 WebSocket 連線（async 版本）

    可安全忽略伺服器未送出 close frame 的情況（ConnectionClosedOK）
    """
    try:
        await ws.close()
        print("[INFO] 🔌 WS 連線已關閉")
    except ConnectionClosedOK:
        # ✅ 忽略伺服器沒送 close frame 的狀況，不列為錯誤
        print("[INFO] 🔕 WS client 已關閉，但未收到 close frame（可忽略）")
    except Exception as e:
        print(f"[ERROR] ❌ 關閉 WS 失敗：{e}")



async def start_ws_async(ws: WebSocketClientProtocol) -> None:
    """
    啟動 WebSocket 封包接收循環，模擬 thread 模式的 run_forever 行為。
    - 每收到一包封包就會自動呼叫 dispatcher
    - 若收到錯誤會自動結束並觸發 callback
    """
    async def _recv_loop():
        try:
            while True:
                raw_msg = await ws.recv()
                await dispatch_event(raw_msg, ws)

        except ConnectionClosedOK:
            print("[start_ws_async] ✅ WebSocket 已正常關閉")

        except ConnectionClosedError as e:
            print(f"[start_ws_async] ⚠️ WebSocket 已關閉（未握手完成）：{e}")

        except Exception as e:
            print(f"[start_ws_async] ❌ 接收封包過程出錯：{e}")

        # 🟡 結束時觸發 callback_done（不論何種關閉）
        if hasattr(ws, "callback_done") and isinstance(ws.callback_done, asyncio.Event):
            if not ws.callback_done.is_set():
                ws.callback_done.set()

    asyncio.create_task(_recv_loop())

