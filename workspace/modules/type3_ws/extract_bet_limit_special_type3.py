import os
from workspace.tools.common.result_code import ResultCode

DEBUG = os.getenv("DEBUG_WS_PACKET", "false").lower() == "true"

async def extract_bet_limit_special(ws) -> int:
    """
    處理特殊遊戲封包格式，從 data.game_base_info 擷取 base_bet 或 max_bet。
    """
    try:
        rs = getattr(ws, "rs_data", {})
        data = rs.get("data", {})
        game_base_info = data.get("game_base_info", {})

        mode = os.getenv("BET_LEVEL_MODE", "min").lower()

        if mode == "min":
            value = game_base_info.get("base_bet")
        elif mode == "max":
            value = game_base_info.get("max_bet")
        else:
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

        if isinstance(value, int) and value > 0:
            ws.bet_limit = value
            if DEBUG:
                from workspace.tools.printer.printer import print_info
                print_info(f"[DEBUG] 特殊限紅擷取成功：{value}")
            return ResultCode.SUCCESS
        else:
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

    except Exception:
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED
