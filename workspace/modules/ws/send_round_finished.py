import json
from websocket import WebSocketApp
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info  # 可移除後期用

def send_round_finished(ws: WebSocketApp) -> int:
    """
    發送 cur_round_finished 封包，不驗回傳內容。
    callback 處理由子控註冊 handle_round_finished_ack。
    """
    payload = {"event": "cur_round_finished"}
    payload_str = json.dumps(payload)
    ws.send(payload_str)

    return ResultCode.SUCCESS


def handle_round_finished_ack(ws: WebSocketApp, message: str) -> None:
    """
    收到 cur_round_finished 回應的 handler，不驗內容。
    """
    if hasattr(ws, "callback_done"):
        ws.callback_done.set()
