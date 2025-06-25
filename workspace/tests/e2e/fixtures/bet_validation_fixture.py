# workspace/tests/e2e/fixtures/bet_validation_fixture.py

from workspace.controller.ws.ws_connection_controller import ws_connection_flow
from workspace.tools.common.result_code import ResultCode

def run_ws_bet_flow(account: str, oid: str) -> dict:
    """
    執行單一 OID 的 WebSocket 子控流程，回傳下注驗證資料。
    取得 join_room 的四參數與 bet_response 的 expected / actual。
    """
    try:
        code = ws_connection_flow(account=account, oid=oid)

        result = {
            "account": account,
            "oid": oid,
            "error_code": code,
            "expected": None,
            "actual": None,
            "level": None,
            "lines": None,
            "coin": None,
            "value": None,
        }

        # 嘗試從 ws 中提取上下文資料
        from websocket import WebSocketApp
        ws = getattr(ws_connection_flow, "last_ws", None)

        if ws:
            if hasattr(ws, "bet_context"):
                result.update(ws.bet_context)  # 提供 level, lines, coin, value, total_bet
            if hasattr(ws, "bet_result"):
                result.update(ws.bet_result)   # 提供 expected, actual, error_

        return result

    except Exception as e:
        return {
            "account": account,
            "oid": oid,
            "error_code": -99999,
            "expected": None,
            "actual": None,
            "level": None,
            "lines": None,
            "coin": None,
            "value": None,
            "exception": str(e),
        }
