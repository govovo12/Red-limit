import threading
from typing import Callable, Tuple
from websocket import WebSocketApp
import websocket
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode


def connect_ws(
    ws_url: str,
    origin: str,
    on_message: Callable
) -> Tuple[int, WebSocketApp]:
    """
    工具模組：建立 WebSocket 連線
    - 不負責組 callback，只負責使用傳入的 callback
    - 不處理 dispatcher 註冊
    """
    print_info(f"🌐 嘗試連線：{ws_url}")

    try:
        ws_app = WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=lambda ws, err: print_error(f"💥 WebSocket 錯誤：{err}"),
            on_close=lambda ws, code, msg: print_info(f"🔌 WebSocket 關閉：{code} / {msg}"),
            on_open=lambda ws: print_info("✅ WebSocket 成功建立")
        )

        # 在背景 thread 中啟動 WebSocket 連線
        ws_thread = threading.Thread(target=ws_app.run_forever, kwargs={
            "origin": origin,
            "ping_interval": 30,
            "ping_timeout": 10,
        })
        ws_thread.daemon = True
        ws_thread.start()

        return ResultCode.SUCCESS, ws_app

    except Exception as e:
        print_error(f"❌ 建立 WebSocket 連線失敗：{e}")
        return ResultCode.TASK_WS_CONNECTION_FAILED, None

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