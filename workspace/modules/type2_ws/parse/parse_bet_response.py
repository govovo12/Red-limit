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
    從 bet_ack 封包中擷取 bet 值，失敗時設定為 -1。
    """
    try:
        data = message if isinstance(message, dict) else json.loads(message)
        bet = data.get("game_result", {}).get("bet")
        ws.bet_ack_data = {"bet": bet if bet is not None else -1}
    except Exception:
        ws.bet_ack_data = {"bet": -1}
        ws.raw_packet = message  # 捕捉解析失敗時的原始封包

    return ws.bet_ack_data


async def handle_bet_ack(ws, message: Union[str, dict]) -> int:
    result = {
        "expected": None,  # total_bet
        "actual": None,    # server 回傳 bet 值
        "rule": None,      # ✅ 額外補上限紅規則
        "formula": None,   # ✅ 額外補上下注組合公式（可選）
        "error_code": None
    }

    try:
        # Step 1: 擷取實際下注金額
        response = await extract_bet_value_from_response(ws, message)
        actual = response.get("bet")
        expected = ws.bet_context.get("total_bet") if hasattr(ws, "bet_context") else None
        formula = ws.bet_context.get("formula") if hasattr(ws, "bet_context") else None

        result.update({
            "expected": expected,
            "actual": actual,
            "formula": formula,
        })

        # Step 2: 檢查資料完整性
        if expected is None or actual is None:
            result["error_code"] = ResultCode.TASK_BET_ACK_DATA_INCOMPLETE
            ws.raw_packet = message
            return finalize(ws, result)

        # Step 3: 型別轉換與一致性檢查
        try:
            actual_f = float(actual)
            expected_f = float(expected)
        except Exception:
            result["error_code"] = ResultCode.TASK_BET_ACK_PARSE_FAILED
            ws.raw_packet = message
            return finalize(ws, result)

        if not math.isclose(actual_f, expected_f, rel_tol=1e-5):
            result["error_code"] = ResultCode.TASK_BET_MISMATCHED
            return finalize(ws, result)

        # Step 4: 檢查是否符合限紅規則
        try:
            result["rule"] = BET_AMOUNT_RULE  # ✅ 儲存原始限紅規則
            if not check_bet_amount_rule(BET_AMOUNT_RULE, actual_f):
                result["error_code"] = ResultCode.TASK_BET_AMOUNT_VIOLATED
            else:
                result["error_code"] = ResultCode.SUCCESS
        except Exception:
            result["error_code"] = ResultCode.TASK_BET_ACK_PARSE_FAILED
            ws.raw_packet = message

    except Exception:
        result["error_code"] = ResultCode.TASK_BET_ACK_PARSE_FAILED
        ws.raw_packet = message

    return finalize(ws, result)


def finalize(ws, result: dict) -> int:
    """
    將處理結果寫入 ws 對象並觸發 callback。
    """
    ws.error_code = result["error_code"]
    ws.bet_result = result

    if hasattr(ws, "callback_done") and not ws.callback_done.is_set():
        ws.callback_done.set()

    return result["error_code"]
