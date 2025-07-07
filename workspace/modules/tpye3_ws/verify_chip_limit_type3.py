import os
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info


def verify_chip_limit_from_packet(rs: dict) -> tuple[int, int | None]:
    """
    擷取封包中的限紅資訊並回傳 (錯誤碼, bet_limit)。
    - 先從 data["game_chips"] / ["area_max_bet"] 擷取
    - 若無則 fallback 到 data["init_info"]["game_chips"]
    - 若擷取失敗，回傳 (錯誤碼, None)
    """
    try:
        mode = os.getenv("BET_LEVEL_MODE", "min").lower()
        data = rs.get("data", {})

        value = None
        if mode == "min":
            value = data.get("game_chips")
        elif mode == "max":
            value = data.get("area_max_bet")

        # fallback 到 init_info
        if not value:
            init_info = data.get("init_info", {})
            if isinstance(init_info, dict):
                if mode == "min":
                    value = init_info.get("game_chips")
                elif mode == "max":
                    value = init_info.get("area_max_bet")

        if not value or not isinstance(value, list):
            print_info(f"[DEBUG] 擷取失敗，value={value}")
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED, None

        selected = value[0]
        print_info(f"🎯 bet_limit = {selected}")
        return ResultCode.SUCCESS, selected

    except Exception as e:
        print_info(f"[EXCEPTION] 限紅驗證錯誤：{e}")
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED, None
