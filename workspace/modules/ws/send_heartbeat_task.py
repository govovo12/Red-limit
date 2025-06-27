import json
from websocket import WebSocketApp
from workspace.tools.printer.printer import print_info
from workspace.tools.common.result_code import ResultCode

HEARTBEAT_PAYLOAD = {"event": "keep_alive"}

def send_heartbeat(ws: WebSocketApp) -> int:
    """
    發送心跳封包，不驗內容，僅等待伺服器回應。
    callback 處理由子控負責註冊。
    """
    print_info("❤️ 發送心跳封包")
    ws.send(json.dumps(HEARTBEAT_PAYLOAD))
    return ResultCode.SUCCESS


def handle_heartbeat_response(ws: WebSocketApp, message: str) -> None:
    """
    處理心跳回應封包（只確認有回應，不驗內容）。
    子控需先設定 ws.callback_done。
    """
    print_info("✅ 收到心跳回應（不驗內容）")
    if hasattr(ws, "callback_done"):
        ws.callback_done.set()