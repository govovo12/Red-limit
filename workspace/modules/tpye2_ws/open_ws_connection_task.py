# workspace/modules/tpye2_ws/open_ws_connection_task.py

import asyncio
from typing import Tuple, Optional

from workspace.tools.ws.ws_connection_async_helper import open_ws_connection
from workspace.tools.common.result_code import ResultCode


async def open_ws_connection_task(ws_url: str, origin: str) -> Tuple[int, Optional[any]]:
    """
    建立 WebSocket 連線，並初始化 ws client 資訊（oid, callback）

    Returns:
        Tuple[int, Optional[WebSocketClient]]
    """
    try:
        ws_or_code = await open_ws_connection(ws_url=ws_url, origin=origin)
        print(f"🧪 DEBUG ws_url={ws_url}")
        print(f"🧪 DEBUG origin={origin}")

        if isinstance(ws_or_code, int):  # 錯誤碼
            return ws_or_code, None

        ws = ws_or_code
        oid = ws_url.split("oid=")[-1]
        ws.oid = oid
        ws.callback_done = asyncio.Event()

        return ResultCode.SUCCESS, ws

    except Exception:
        return ResultCode.TASK_OPEN_WS_CONNECTION_FAILED, None
