# workspace/tools/ws/ws_connection_helper.py

import websocket
from websocket import WebSocketApp
from typing import Callable, Tuple
import threading

from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode


def connect_ws(
    ws_url: str,
    origin: str,
    on_message: Callable
) -> Tuple[int, WebSocketApp]:
    """
    工具模組：建立 WebSocket 連線（只建立，不啟動）
    - 回傳 ws 實例，由外部決定何時啟動
    """
    print_info(f"🌐 初始化 WebSocket：{ws_url}")

    try:
        def _on_error(ws, err):
            print_error(f"💥 WebSocket 錯誤：{err}")
            ws.error_code = ResultCode.TASK_WS_CONNECTION_FAILED

        ws_app = WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=_on_error,
            on_close=lambda ws, code, msg: print_info(f"🔌 WebSocket 關閉：{code} / {msg}"),
            on_open=lambda ws: print_info("✅ WebSocket 成功建立")
        )

        ws_app._origin = origin
        ws_app.ready = False
        ws_app.error_code = ResultCode.SUCCESS

        return ResultCode.SUCCESS, ws_app

    except Exception as e:
        print_error(f"❌ 初始化 WebSocketApp 失敗：{e}")
        return ResultCode.TASK_WS_CONNECTION_FAILED, None


def start_ws(ws: WebSocketApp) -> None:
    """
    明確啟動 WebSocket 執行緒，應在註冊所有事件處理器後呼叫。
    """
    def _run():
        try:
            ws.ready = True
            ws.run_forever(
                origin=getattr(ws, "_origin", None),
                ping_interval=30,
                ping_timeout=10,
            )
        except Exception as e:
            print_error(f"❌ run_forever 出錯：{e}")
            ws.error_code = ResultCode.TASK_WS_CONNECTION_FAILED

    threading.Thread(target=_run, daemon=True).start()


def disconnect_ws(ws):
    """
    關閉 WebSocket 並印出關閉訊息
    """
    try:
        if ws:
            print_info("🔌 關閉 WebSocket 連線")
            ws.close()
    except Exception as e:
        print_error(f"❌ 關閉連線失敗：{e}")
