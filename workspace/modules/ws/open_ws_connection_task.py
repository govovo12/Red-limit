from typing import Tuple
from websocket import WebSocketApp
from threading import Event

from workspace.tools.ws.ws_connection_helper import connect_ws
from workspace.tools.common.result_code import ResultCode


def open_ws_connection_task(ws_url: str, origin: str, done: Event) -> Tuple[int, WebSocketApp]:
    """
    任務模組：建立 WebSocket 連線，回傳 ws 實例，由子控負責註冊事件與 callback。
    """
    # ❌ 不再建立內部 on_message，callback_done 綁定交由子控處理
    code, ws = connect_ws(ws_url=ws_url, origin=origin, on_message=None)

    if code != ResultCode.SUCCESS:
        return code, None

    return ResultCode.SUCCESS, ws
