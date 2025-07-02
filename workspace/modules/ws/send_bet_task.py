# workspace/modules/ws/send_bet_task.py

"""
任務模組（async）：發送 bet 封包，送出所有下注參數（不含 total_bet）
"""

import json
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info


async def send_bet_async(ws) -> int:
    """
    發送 bet 封包（async），送出所有下注參數（不含 total_bet）。
    子控需確保 ws.bet_context 存在。
    """
    if not hasattr(ws, "bet_context"):
        return ResultCode.TASK_DATA_INCOMPLETE

    # 移除空 key 與 total_bet 欄位
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

    try:
        payload_str = json.dumps(bet_payload)
        await ws.send(payload_str)
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_EXCEPTION
