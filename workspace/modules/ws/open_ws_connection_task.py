# workspace/modules/ws/open_ws_connection_task.py

from typing import Tuple, Optional
from websocket import WebSocketApp

from workspace.tools.common.result_code import ResultCode
from workspace.tools.ws.ws_debug_helper import mark_task_start
# ❌ 不再使用 buffer_on_message
# from workspace.tools.ws.ws_debug_helper import buffer_on_message


def open_ws_connection_task(ws_url: str, origin: str) -> Tuple[int, Optional[WebSocketApp]]:
    """
    任務模組：建立 WebSocket 實例但不啟動連線。
    允許子控制器先註冊所有事件處理器後再啟動，避免封包 race condition。
    """
    from workspace.tools.ws.ws_connection_helper import connect_ws

    # ✅ 不傳入 on_message，讓 dispatcher 之後再綁定
    code, ws = connect_ws(ws_url=ws_url, origin=origin, on_message=None)
    if code != ResultCode.SUCCESS:
        return code, None

    ws.oid = ws_url.split("oid=")[-1]
    ws.callback_done = None
    mark_task_start(ws.oid)

    return ResultCode.SUCCESS, ws
