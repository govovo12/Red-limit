"""
Type 1 專用的 fallback 限紅擷取模組
"""

import os
from workspace.tools.common.result_code import ResultCode

DEBUG = os.getenv("DEBUG_WS_FALLBACK", "false").lower() == "true"

def fallback_room_info_chips(ws) -> int:
    mode = os.getenv("BET_LEVEL_MODE", "min").lower()
    room = getattr(ws, "rs_data", {}).get("room_info", {})

    if not isinstance(room, dict):
        return None

    if mode == "min":
        chips = room.get("chips")
        if isinstance(chips, list) and chips:
            return chips[0]
    elif mode == "max":
        red_limit = room.get("red_limit")
        if isinstance(red_limit, list) and len(red_limit) >= 2:
            return red_limit[1]

    return None


def fallback_player_chip_list(ws) -> int:
    mode = os.getenv("BET_LEVEL_MODE", "min").lower()
    rs = getattr(ws, "rs_data", {})
    data = rs.get("data", {})
    account = rs.get("data", {}).get("game_base_info", {}).get("my_account")

    players = data.get("players_info_map", {})
    player_info = players.get(account, {})

    if not isinstance(player_info, dict):
        return None

    if mode == "min":
        chips = player_info.get("chips")
        if isinstance(chips, list) and chips:
            return chips[0]
    return None



async def extract_bet_limit_fallback(ws) -> int:
    """
    fallback 主流程：每個策略自行解析 ws.rs_data 結構
    """
    try:
        strategies = [
            fallback_room_info_chips,
            fallback_player_chip_list,
            
        ]

        for strategy in strategies:
            value = strategy(ws)
            if isinstance(value, int) and value > 0:
                print(f"[fallback ✅] 使用 {strategy.__name__} 命中限紅：{value}")
                ws.bet_limit = value
                return ResultCode.SUCCESS

        print(f"[fallback ❌] 所有策略失敗：oid={ws.oid} game={ws.game_name}")
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

    except Exception:
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

