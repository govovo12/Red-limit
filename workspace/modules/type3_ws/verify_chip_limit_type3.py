import os
from workspace.tools.common.result_code import ResultCode

async def verify_chip_limit(ws) -> int:
    """
    擷取標準限紅欄位：game_chips / area_max_bet
    """
    try:
        rs = getattr(ws, "rs_data", {})
        data = rs.get("data", {})
        mode = os.getenv("BET_LEVEL_MODE", "min").lower()

        if mode == "min":
            value = data.get("game_chips")
        elif mode == "max":
            value = data.get("area_max_bet")
        else:
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

        if isinstance(value, list):
            selected = value[0] if value else None
        elif isinstance(value, int):
            selected = value
        else:
            selected = None

        if not selected or not isinstance(selected, int):
            print("[DEBUG] verify_chip_limit() 抓不到標準欄位，準備 fallback")
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

        ws.bet_limit = selected
        return ResultCode.SUCCESS
        
    except Exception:
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

