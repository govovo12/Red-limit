# workspace/modules/ws/parse_bet_response.py

import json
from typing import Union
from websocket import WebSocketApp
import math

from workspace.tools.common.result_code import ResultCode
from workspace.tools.assertion.rule_checker import check_bet_amount_rule
from workspace.tools.env.config_loader import BET_AMOUNT_RULE
from workspace.tools.printer.printer import print_info


def extract_bet_value_from_response(ws: WebSocketApp, message: Union[str, dict]) -> dict:
    """
    從伺服器回應封包中提取 bet 欄位的值(float)
    """
    try:
        data = message if isinstance(message, dict) else json.loads(message)

        bet = data.get("game_result", {}).get("bet")

 

        ws.bet_ack_data = {"bet": bet if bet is not None else -1}
    except Exception as e:
      
        ws.bet_ack_data = {"bet": -1}

    if hasattr(ws, "callback_done"):
        ws.callback_done.set()

    return ws.bet_ack_data



def handle_bet_ack(ws: WebSocketApp, message: Union[str, dict]) -> int:
    """
    處理伺服器 bet 封包回應，並驗證下注金額正確與是否符合限紅規則。
    設定 ws.error_code 與 ws.bet_result。
    """
    result = {"bet": -1, "expected": None, "actual": None, "error_code": None}

    try:
        response = extract_bet_value_from_response(ws, message)
        actual = response.get("bet")
        expected = ws.bet_context.get("total_bet") if hasattr(ws,"bet_context") else None

        result.update({
            "expected": expected,
            "actual": actual,
        })
        print(f"[DEBUG] 驗證金額：expected={expected}, actual={actual}")

        if expected is None or actual is None:
            result["error_code"] = ResultCode.TASK_DATA_INCOMPLETE

        elif not math.isclose(float(actual), float(expected), rel_tol=1e-9):
            result["error_code"] = ResultCode.TASK_BET_MISMATCHED

        elif not check_bet_amount_rule(BET_AMOUNT_RULE, actual):
            result["error_code"] = ResultCode.TASK_BET_AMOUNT_RULE_VIOLATED

        else:
            result["error_code"] = ResultCode.SUCCESS

    except Exception:
        if result.get("error_code") is None:
            result["error_code"] = ResultCode.TASK_EXCEPTION

    ws.error_code = result["error_code"]
    ws.bet_result = result

    if hasattr(ws, "callback_done"):
        ws.callback_done.set()

    return result["error_code"]
