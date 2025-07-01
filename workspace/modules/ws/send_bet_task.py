import json
from websocket import WebSocketApp
from decimal import Decimal
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info


def send_bet_task(ws: WebSocketApp) -> int:
    """
    發送 bet 封包，送出所有下注參數（不含 total_bet）。
    """
    if not hasattr(ws, "bet_context"):
        return ResultCode.TASK_DATA_INCOMPLETE

    # 清理欄位名稱，移除 total_bet 與空白 key
    excluded_keys = {"total_bet"}
    context = {k.strip(): v for k, v in ws.bet_context.items()}
    filtered_context = {
        k: v for k, v in context.items()
        if k not in excluded_keys and v is not None
    }

    bet_payload = {
        "event": "bet",
        **filtered_context
    }

    # ✅ Debug 印出實際送出的封包內容
    #print_info(f"[DEBUG] 發送 bet 封包內容：{json.dumps(bet_payload, ensure_ascii=False)}")

    try:
        payload_str = json.dumps(bet_payload)
        ws.send(payload_str)
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_EXCEPTION
