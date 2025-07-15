import os
from workspace.tools.common.result_code import ResultCode


def fallback_game_chips_then_max_bet(init_info: dict) -> int:
    """
    fallback 結構 V2：
    - min 模式抓 game_chips[0]
    - max 模式抓 area_max_bet[0]
    """
    mode = os.getenv("BET_LEVEL_MODE", "min").lower()
    if mode == "min":
        values = init_info.get("game_chips", [])
    elif mode == "max":
        values = init_info.get("area_max_bet", [])
    else:
        return None

    if isinstance(values, list) and values:
        return values[0]
    return None


def fallback_area_min_max(init_info: dict) -> int:
    """
    fallback 結構 V1（原始仙家類型）：
    - min 模式抓 area_min_bet[0]
    - max 模式抓 area_max_bet[0]
    """
    mode = os.getenv("BET_LEVEL_MODE", "min").lower()
    if mode == "min":
        values = init_info.get("area_min_bet", [])
    elif mode == "max":
        values = init_info.get("area_max_bet", [])
    else:
        return None

    if isinstance(values, list) and values:
        return values[0]
    return None


async def extract_bet_limit_fallback(ws) -> int:
    """
    多種結構 fallback 支援，按順序執行直到成功為止
    """
    try:
        rs = getattr(ws, "rs_data", {})
        data = rs.get("data", {})
        init_info = data.get("init_info", {})

        strategies = [
            fallback_game_chips_then_max_bet,  # ✅ 最優先：新觀察到的結構
            fallback_area_min_max,             # 第二優先：原本仙家結構
        ]

        for strategy in strategies:
            value = strategy(init_info)
            if isinstance(value, int) and value > 0:
                print(f"[fallback ✅] 使用 {strategy.__name__} 命中限紅：{value}")
                ws.bet_limit = value
                return ResultCode.SUCCESS

        print(f"[fallback ❌] 全部策略失敗：{ws.game_name} oid={ws.oid} keys={list(init_info.keys())}")
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

    except Exception:
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED
