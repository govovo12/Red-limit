# workspace/modules/ws/send_bet_task.py

import json
from websocket import WebSocketApp

from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info, print_error


def send_bet_task(ws: WebSocketApp) -> int:
    """
    發送下注封包。使用 bet_context 組成封包並傳送。
    若失敗則設定錯誤碼並回傳。
    """
    if not hasattr(ws, "bet_context"):
        print_error("❌ 缺少 bet_context，無法下注")
        return ResultCode.TASK_BET_CONTEXT_MISSING

    context = ws.bet_context

    # 排除不應傳送的欄位
    excluded_keys = {"total_bet"}
    filtered_context = {
        k: v for k, v in context.items()
        if k not in excluded_keys and v is not None
    }

    bet_payload = {
        "event": "bet",
        **filtered_context
    }

    try:
        payload_str = json.dumps(bet_payload)
        print_info(f"🎯 發送下注封包：{payload_str}")
        ws.send(payload_str)
        return ResultCode.SUCCESS
    except Exception as e:
        print_error(f"❌ 發送下注封包失敗：{e}")
        return ResultCode.TASK_SEND_BET_FAILED
