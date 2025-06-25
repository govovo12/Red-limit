import json
from websocket import WebSocketApp
from workspace.tools.printer.printer import print_error,print_info
from workspace.tools.common.result_code import ResultCode

def extract_bet_value_from_response(ws: WebSocketApp, message: str) -> dict:
    """
    從伺服器回應封包中提取 bet 欄位的值(float)
    """
    try:
        data = json.loads(message)
        bet = data.get("game_result", {}).get("bet")
        if bet is not None:
            ws.bet_ack_data = {"bet": bet}
        else:
            print_error("⚠️ bet_ack 缺少 game_result.bet 欄位")
            ws.bet_ack_data = {"bet": -1}
    except json.JSONDecodeError:
        print_error("❌ bet_ack JSON 解析失敗")
        ws.bet_ack_data = {"bet": -1}

    if hasattr(ws, "callback_done"):
        ws.callback_done.set()

    return ws.bet_ack_data  


def handle_bet_ack(ws: WebSocketApp, message: str) -> dict:
    """
    處理伺服器 bet 封包回應，並驗證下注金額正確
    """
    result = {"bet": -1, "expected": None, "actual": None, "error_code": None}

    try:
        response = extract_bet_value_from_response(ws, message)
        actual = response.get("bet")
        expected = ws.bet_context.get("total_bet")

        result.update({
            "expected": expected,
            "actual": actual,
        })

        if actual != expected:
            print_error(f"❌ 金額不一致：期望 {expected}，實際 {actual}")
            result["error_code"] = ResultCode.TASK_ASSERT_VALUE_MISMATCH
            ws.error_code = ResultCode.TASK_ASSERT_VALUE_MISMATCH
        else:
            print_info(f"✅ 金額正確：{actual}")
            result["error_code"] = ResultCode.SUCCESS

    except Exception as e:
        print_error(f"❌ extract_bet_value_from_response 發生例外: {e}")
        result["error_code"] = ResultCode.TASK_EXCEPTION

    # ✅ 將比對結果掛到 ws 對象上，方便 E2E 測試 fixture 使用
    ws.bet_result = result

    if hasattr(ws, "callback_done"):
        ws.callback_done.set()

    return result


