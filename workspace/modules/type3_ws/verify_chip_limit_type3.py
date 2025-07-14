import os
from workspace.tools.common.result_code import ResultCode

async def verify_chip_limit(ws) -> int:
    """
    從 ws.rs_data 中擷取限紅資料，支援正常與特殊結構。
    根據 .env 的 BET_LEVEL_MODE 決定抓哪個欄位。
    """
    try:
        rs = getattr(ws, "rs_data", {})
        data = rs.get("data", {})
        mode = os.getenv("BET_LEVEL_MODE", "min").lower()

        value = None

        # ✅ 正常結構
        if mode == "min":
            value = data.get("game_chips")
        elif mode == "max":
            value = data.get("area_max_bet")

        # ✅ fallback 結構（init_info）
        if not value:
            init_info = data.get("init_info", {})
            if isinstance(init_info, dict):
                if mode == "min":
                    value = init_info.get("game_chips")
                elif mode == "max":
                    value = init_info.get("area_max_bet")

        # ✅ fallback 結構（特殊遊戲封包：game_base_info）
        if not value:
            game_base_info = data.get("game_base_info", {})
            if isinstance(game_base_info, dict):
                if mode == "min":
                    value = game_base_info.get("base_bet")
                elif mode == "max":
                    value = game_base_info.get("max_bet")

        # ✅ 統一格式與安全檢查
        if isinstance(value, list):
            selected = value[0] if value else None
        elif isinstance(value, int):
            selected = value
        else:
            selected = None

        if not selected or not isinstance(selected, int):
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

        ws.bet_limit = selected
        return ResultCode.SUCCESS

    except Exception:
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED
