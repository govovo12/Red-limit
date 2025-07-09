"""
任務模組（async）：發送 bet 封包，送出所有下注參數（不含 total_bet）
"""

# === 標準工具 ===
import json

# === 錯誤碼 ===
from workspace.tools.common.result_code import ResultCode


async def send_bet_async(ws) -> int:
    """
    發送 bet 封包（async），送出所有下注參數（不含 total_bet）。
    子控需確保 ws.bet_context 存在。

    Args:
        ws: WebSocket 對象（需含 bet_context）

    Returns:
        int: ResultCode.SUCCESS 或錯誤碼
    """
    if not hasattr(ws, "bet_context"):
        return ResultCode.TASK_BET_CONTEXT_MISSING

    try:
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

        payload_str = json.dumps(bet_payload)
        await ws.send(payload_str)
        return ResultCode.SUCCESS

    except Exception:
        return ResultCode.TASK_SEND_BET_FAILED
