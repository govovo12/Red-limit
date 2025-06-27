import json
from websocket import WebSocketApp
from workspace.tools.common.result_code import ResultCode

def send_bet_task(ws: WebSocketApp) -> int:
    """
    發送下注封包，不驗回傳內容，並返回錯誤碼。
    callback 處理由子控註冊 handle_bet_ack。
    """
    if not hasattr(ws, "bet_context"):
        return ResultCode.TASK_BET_CONTEXT_MISSING

    context = ws.bet_context

    # 排除 total_bet，不應包含在下注封包中
    excluded_keys = {"total_bet"}
    filtered_context = {
        k: v for k, v in context.items()
        if k not in excluded_keys and v is not None
    }

    bet_payload = {
        "event": "bet",
        **filtered_context
    }

    payload_str = json.dumps(bet_payload)
    # 不再打印發送訊息
    ws.send(payload_str)

    return ResultCode.SUCCESS
