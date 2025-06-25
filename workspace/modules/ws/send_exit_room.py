import json
from websocket import WebSocketApp
from workspace.tools.printer.printer import print_info
from workspace.tools.common.result_code import ResultCode

def send_exit_room(ws: WebSocketApp) -> int:
    """
    發送 exit_room 封包，不驗回傳內容。
    callback 處理由子控註冊 handle_exit_room_ack。
    """
    payload = {"event": "exit_room"}
    payload_str = json.dumps(payload)
    print_info(f"📤 發送 exit_room 封包：{payload_str}")
    ws.send(payload_str)
    return ResultCode.SUCCESS


def handle_exit_room_ack(ws: WebSocketApp, message: str) -> None:
    """
    收到 exit_room 封包的伺服器回應（不驗內容）。
    """
    print_info("✅ 收到 exit_room 回應（不驗內容）")
    if hasattr(ws, "callback_done"):
        ws.callback_done.set()
