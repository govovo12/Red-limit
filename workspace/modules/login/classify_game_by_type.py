from workspace.tools.common.result_code import ResultCode


def classify_game_by_type(game_type_map: dict, game_data_list: list) -> tuple[int, dict]:
    """
    根據 game_code 所屬類型，將遊戲分類為 type_1~type_4，回傳 type 對應的 oid + game_name 清單。

    Args:
        game_type_map (dict): 四類 type ➜ set of game_code
        game_data_list (list): 遊戲清單，每筆含 game_code, game_name, oid

    Returns:
        tuple: (錯誤碼, {type_n: [ {oid, game_name, game_option_list_type, room_id}, ... ]})
    """
    try:
        result = {
            "type_1": [],
            "type_2": [],
            "type_3": [],
            "type_4": [],
        }

        for game in game_data_list:
            code = game.get("game_code")
            name = game.get("game_name")
            oid = game.get("oid")
            option_type = game.get("game_option_list_type")
            room_id = game.get("room_id")

            if not code or not name or not oid:
                continue  # 忽略不完整資料

            for type_key, code_set in game_type_map.items():
                if code in code_set:
                    result[type_key].append({
                        "oid": oid,
                        "game_name": name,
                        "game_option_list_type": option_type,
                        "room_id": room_id
                    })
                    break

        return ResultCode.SUCCESS, result

    except Exception:
        return ResultCode.TASK_EXCEPTION, {}
