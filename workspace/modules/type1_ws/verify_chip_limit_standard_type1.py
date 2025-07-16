"""
擷取 Type 1 遊戲的標準限紅（從 game_info.bet_money_list 中擷取）
"""

import os
from workspace.tools.common.result_code import ResultCode

async def verify_chip_limit(ws) -> int:
    """
    擷取 Type 1 遊戲的下注限紅：game_info -> bet_money_list
    - 比小：取 bet_money_list[0]
    - 比大：取 bet_money_list[-1]
    """
    try:
        rs = getattr(ws, "rs_data", {})
        data = rs.get("data", {})
        game_info = data.get("game_info", {})
        bet_list = game_info.get("bet_money_list", [])

        if not isinstance(bet_list, list) or not bet_list:
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

        mode = os.getenv("BET_LEVEL_MODE", "min").lower()
        if mode == "min":
            selected = bet_list[0]
        elif mode == "max":
            selected = bet_list[-1]
        else:
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

        if not isinstance(selected, int):
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

        ws.bet_limit = selected
        return ResultCode.SUCCESS

    except Exception:
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED
