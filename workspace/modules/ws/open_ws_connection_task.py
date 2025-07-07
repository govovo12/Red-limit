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
    try:
        print(f"[DEBUG] 🛰️ 準備建立連線: {ws_url} origin={origin}")
        ws_or_code = await open_ws_connection(ws_url=ws_url, origin=origin)

        # 如果是錯誤碼，直接往上拋（由工具模組決定）
        if isinstance(ws_or_code, int):
            return ws_or_code, None

        ws = ws_or_code
        oid = ws_url.split("oid=")[-1]
        ws.oid = oid
        ws.callback_done = asyncio.Event()
        mark_task_start(oid)

        return ResultCode.SUCCESS, ws

    except Exception as e:
        print(f"[TASK] ❌ 任務模組發生例外：{e}")
        return ResultCode.TASK_OPEN_WS_CONNECTION_FAILED, None

