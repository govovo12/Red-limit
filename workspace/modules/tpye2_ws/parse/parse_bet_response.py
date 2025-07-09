"""
任務模組（async）：解析伺服器 bet 回應封包，並驗證下注金額與限紅規則
"""

# === 標準工具 ===
import json
import math
from typing import Union

# === 錯誤碼與工具 ===
from workspace.tools.common.result_code import ResultCode
from workspace.tools.assertion.rule_checker import check_bet_amount_rule
from workspace.tools.env.config_loader import BET_AMOUNT_RULE


async def extract_bet_value_from_response(ws, message: Union[str, dict]) -> dict:
    """
    從伺服器回應封包中提取 bet 欄位的值(float)，若失敗則預設為 -1

    Args:
        ws: WebSocket 物件
        message: 原始封包（dict 或 JSON 字串）

    Returns:
        dict: {"bet": float}
    """
    try:
        data = message if isinstance(message, dict) else json.loads(message)
        bet = data.get("game_result", {}).get("bet")
        ws.bet_ack_data = {"bet": bet if bet is not None else -1}
    except Exception:
        ws.bet_ack_data = {"bet": -1}

    if hasattr(ws, "callback_done"):
        ws.callback_done.set()

    return ws.bet_ack_data


async def handle_bet_ack(ws, message: Union[str, dict]) -> int:
    """
    處理伺服器 bet 封包回應，驗證下注金額與限紅合法性。
    設定 ws.error_code 與 ws.bet_result。

    Args:
        ws: WebSocket 物件（需含 bet_context）
        message: 回應封包（dict 或 JSON 字串）

    Returns:
        int: ResultCode
    """
    result = {"bet": -1, "expected": None, "actual": None, "error_code": None}

    try:
        response = await extract_bet_value_from_response(ws, message)
        actual = response.get("bet")
        expected = ws.bet_context.get("total_bet") if hasattr(ws, "bet_context") else None

        result.update({
            "expected": expected,
            "actual": actual,
        })

        if expected is None or actual is None:
            result["error_code"] = ResultCode.TASK_BET_ACK_DATA_INCOMPLETE

        elif not math.isclose(float(actual), float(expected), rel_tol=1e-9):
            result["error_code"] = ResultCode.TASK_BET_MISMATCHED

        elif not check_bet_amount_rule(BET_AMOUNT_RULE, actual):
            result["error_code"] = ResultCode.TASK_BET_AMOUNT_VIOLATED

        else:
            result["error_code"] = ResultCode.SUCCESS

    except Exception:
        result["error_code"] = ResultCode.TASK_BET_ACK_PARSE_FAILED

    ws.error_code = result["error_code"]
    ws.bet_result = result

    if hasattr(ws, "callback_done"):
        ws.callback_done.set()

    return result["error_code"]
