import os
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info

DEBUG = False  # 永遠開啟 debug 印出

async def extract_bet_limit_special(ws) -> int:
    try:
        rs = getattr(ws, "rs_data", {})
        mode = os.getenv("BET_LEVEL_MODE", "min").lower()
        value = None

        # ✅ fallback 1: init_info
        init_info = rs.get("data", {}).get("init_info") or rs.get("init_info")
        if isinstance(init_info, dict):
            if mode == "min":
                value = init_info.get("game_chips")
            elif mode == "max":
                value = init_info.get("area_max_bet")
            print_info(f"[DEBUG] init_info 嘗試擷取：{value}")

        # ✅ fallback 2: game_base_info（min 改抓 players_info_map）
        if value is None:
            game_base_info = rs.get("data", {}).get("game_base_info") or rs.get("game_base_info")
            if isinstance(game_base_info, dict):
                if mode == "min":
                    pf_account = getattr(ws, "pf_account", None)
                    if not pf_account:
                        print_info("[DEBUG] ❌ ws.pf_account 為空，無法擷取 players_info_map")
                    else:
                        players_map = rs.get("data", {}).get("players_info_map", {})
                        player_info = players_map.get(pf_account, {})
                        chips = player_info.get("chips")
                        print_info(f"[DEBUG] pf_account = {pf_account}")
                        print_info(f"[DEBUG] players_info_map chips = {chips}")
                        if isinstance(chips, list) and len(chips) > 0:
                            value = chips[0]
                            print_info(f"[DEBUG] ✅ 從 players_info_map 擷取成功：{value}")
                        else:
                            print_info("[DEBUG] ❌ 無法從 players_info_map 擷取 chips")
                elif mode == "max":
                    value = game_base_info.get("max_bet")
                    print_info(f"[DEBUG] game_base_info max_bet 擷取：{value}")

        # ✅ fallback 3: 最終 fallback → min: room_info.chips[0]，max: red_limit[1]
        if value is None:
            room_info = rs.get("data", {}).get("room_info") or rs.get("room_info")
            if isinstance(room_info, dict):
                chips = room_info.get("chips")
                red_limit = room_info.get("red_limit")
                print_info(f"[DEBUG] fallback chips 原始資料：{chips}")
                print_info(f"[DEBUG] fallback red_limit 原始資料：{red_limit}")

                if mode == "min":
                    if isinstance(chips, list) and len(chips) > 0:
                        value = chips[0]
                        print_info(f"[DEBUG] ✅ 從 room_info.chips[0] 擷取成功：{value}")
                    else:
                        print_info("[DEBUG] ❌ chips 結構錯誤，無法擷取 min")
                elif mode == "max":
                    if isinstance(red_limit, list) and len(red_limit) > 1:
                        value = red_limit[1]
                        print_info(f"[DEBUG] ✅ 從 red_limit[1] 擷取成功：{value}")
                    else:
                        print_info("[DEBUG] ❌ red_limit 結構錯誤，無法擷取 max")

        # ✅ 統一格式與型別檢查
        if isinstance(value, list):
            selected = value[0] if value else None
        elif isinstance(value, int):
            selected = value
        else:
            selected = None

        print_info(f"[DEBUG] 最終 selected = {selected} (type={type(selected)})")

        if not selected or not isinstance(selected, int):
            print_info("[DEBUG] fallback 擷取失敗，selected 無效")
            return ResultCode.TASK_LIMIT_EXTRACTION_FAILED

        ws.bet_limit = selected
        print_info(f"[DEBUG] fallback 限紅擷取成功：{selected}")
        return ResultCode.SUCCESS

    except Exception as e:
        print_info(f"[DEBUG] fallback 發生例外：{e}")
        return ResultCode.TASK_LIMIT_EXTRACTION_FAILED
