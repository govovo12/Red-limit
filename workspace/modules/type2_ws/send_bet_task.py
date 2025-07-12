# workspace/modules/ws/send_bet_task.py

"""
任務模組（async）：發送 bet 封包，送出所有下注參數（不含 total_bet）
"""

# === 標準工具 ===
import json

# === 錯誤碼 ===
from workspace.tools.common.result_code import ResultCode


async def send_bet_async(ws, payload: dict) -> int:
    """
    發送 bet 封包（async），送出所有下注參數（不含 total_bet）

    Args:
        ws: WebSocket 對象
        payload (dict): 下注參數（由子控傳入）

    Returns:
        int: ResultCode.SUCCESS 或錯誤碼
    """
    if not payload or not isinstance(payload, dict):
        return ResultCode.TASK_BET_CONTEXT_MISSING

    try:
        excluded_keys = {"total_bet"}
        filtered_payload = {
            k.strip(): v for k, v in payload.items()
            if k.strip() not in excluded_keys and v is not None
        }

        bet_payload = {
            "event": "bet",
            **filtered_payload
        }

        payload_str = json.dumps(bet_payload)
        await ws.send(payload_str)
        return ResultCode.SUCCESS

    except Exception:
        return ResultCode.TASK_SEND_BET_FAILED
