# workspace/tools/ws/ws_connection_helper.py

import websocket
from websocket import WebSocketApp
from typing import Callable, Tuple
import threading

from workspace.tools.common.result_code import ResultCode


def connect_ws(ws_url: str, origin: str, on_message: Callable) -> Tuple[int, WebSocketApp]:
    """
    工具模組：建立 WebSocket 連線（只建立，不啟動）
    - 回傳 ws 實例，由外部決定何時啟動
    """
    try:
        from workspace.tools.printer.printer import print_info, print_error

        # ✅ 印出連線參數
        #print_info("🧩 建立 WebSocket 連線時使用參數：")
        #print_info(f"🔗 ws_url: {ws_url}")
        #print_info(f"🌐 origin: {origin}")

        def _on_error(ws, err):
            print_error(f"[connect_ws] WebSocket 發生異常：{repr(err)}")

            # 額外印出握手回應 headers（如果有）
            try:
                if hasattr(ws, 'sock') and ws.sock and ws.sock.headers:
                    print_error("[connect_ws] 握手回應 headers：")
                    for k, v in ws.sock.headers.items():
                        print_error(f"{k}: {v}")
            except Exception as e:
                print_error(f"[connect_ws] 無法擷取 headers：{e}")

            ws.error_code = ResultCode.TOOL_WS_ERROR

        ws_app = WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=_on_error,
            on_close=lambda ws, code, msg: None,
            on_open=lambda ws: None
        )

        ws_app._origin = origin
        ws_app.ready = False
        ws_app.error_code = ResultCode.SUCCESS

        return ResultCode.SUCCESS, ws_app

    except Exception:
        return ResultCode.TOOL_WS_CREATE_FAILED, None


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
        except Exception:
            ws.error_code = ResultCode.TOOL_WS_RUN_FAILED

    threading.Thread(target=_run, daemon=True).start()


def disconnect_ws(ws):
    """
    關閉 WebSocket
    """
    try:
        if ws:
            ws.close()
    except Exception:
        pass  # 不設錯誤碼，因為關閉連線失敗通常不影響流程
