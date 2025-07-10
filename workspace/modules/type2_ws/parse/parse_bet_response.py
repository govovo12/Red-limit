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
from workspace.tools.printer.printer import print_info

async def extract_bet_value_from_response(ws, message: Union[str, dict]) -> dict:
    try:
        print_info(f"🧩 [bet_ack] 收到封包 type={type(message)} ws_id={id(ws)}")
        print_info(f"🧩 [bet_ack] 封包內容：{message}")
        data = message if isinstance(message, dict) else json.loads(message)
        bet = data.get("game_result", {}).get("bet")
        ws.bet_ack_data = {"bet": bet if bet is not None else -1}
    except Exception:
        ws.bet_ack_data = {"bet": -1}

    return ws.bet_ack_data  # ❌ 不要在這裡 set callback_done



async def handle_bet_ack(ws, message: Union[str, dict]) -> int:
    result = {"bet": -1, "expected": None, "actual": None, "error_code": None}

    try:
        response = await extract_bet_value_from_response(ws, message)
        actual = response.get("bet")
        expected = ws.bet_context.get("total_bet") if hasattr(ws, "bet_context") else None

        print_info(f"[Debug] 預期 total_bet={expected}({type(expected)}), 實際回傳 bet={actual}({type(actual)})")
        result.update({
            "expected": expected,
            "actual": actual,
        })

        if expected is None or actual is None:
            result["error_code"] = ResultCode.TASK_BET_ACK_DATA_INCOMPLETE
        else:
            try:
                actual_f = float(actual)
                expected_f = float(expected)
                print_info(f"[Debug] 比對用 float 值：expected_f={expected_f}({type(expected_f)}), actual_f={actual_f}({type(actual_f)})")
            except Exception:
                result["error_code"] = ResultCode.TASK_BET_ACK_PARSE_FAILED
                

            if not math.isclose(actual_f, expected_f, rel_tol=1e-5):
                result["error_code"] = ResultCode.TASK_BET_MISMATCHED
            else:
                try:
                    if not check_bet_amount_rule(BET_AMOUNT_RULE, actual_f):
                        result["error_code"] = ResultCode.TASK_BET_AMOUNT_VIOLATED
                    else:
                        result["error_code"] = ResultCode.SUCCESS
                except Exception:
                    result["error_code"] = ResultCode.TASK_BET_ACK_PARSE_FAILED

    except Exception:
        result["error_code"] = ResultCode.TASK_BET_ACK_PARSE_FAILED

    finally:
        ws.error_code = result["error_code"]
        ws.bet_result = result

        if hasattr(ws, "callback_done"):
            print_info(f"[Debug] ✅ callback_done 狀態：{ws.callback_done.is_set()}")
            if not ws.callback_done.is_set():
                ws.callback_done.set()
                print_info(f"[Debug] ✅ callback_done 已 set() 完成")
            else:
                print_info(f"[Debug] ⚠ callback_done 已經被 set 過了")

    return result["error_code"]








