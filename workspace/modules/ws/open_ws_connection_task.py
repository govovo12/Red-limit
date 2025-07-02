"""
任務模組：使用 async 建立 WebSocket 連線（立即啟動）

適用於 async 架構，直接建立並回傳 ws client 物件。
"""

from typing import Tuple, Optional
import asyncio  # ✅ 新增這行
from workspace.tools.ws.ws_connection_async_helper import open_ws_connection
from workspace.tools.common.result_code import ResultCode
from workspace.tools.ws.ws_debug_helper import mark_task_start


async def open_ws_connection_task(ws_url: str, origin: str) -> Tuple[int, Optional[any]]:
    """
    建立 WebSocket 長連線，並包裝 ws 對象
    """
    ws = await open_ws_connection(ws_url=ws_url, origin=origin)
    if not ws:
        return ResultCode.TASK_OPEN_WS_CONNECTION_FAILED, None


    # ✅ 將 oid 提取出來並標記任務開始
    oid = ws_url.split("oid=")[-1]
    ws.oid = oid
    ws.callback_done = asyncio.Event()  # ✅ 加上這行
    mark_task_start(oid)

    return ResultCode.SUCCESS, ws

