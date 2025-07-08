import json
from workspace.tools.network.response_helper import extract_nested
from workspace.tools.common.result_code import ResultCode


def prepare_game_classification_input(response: dict) -> tuple[int, dict, list]:
    """
    將 /get_game_list 的原始 response 拆解成：
    - game_type_map: 各分類對應的 game_code 清單
    - game_data_list: 每筆遊戲對應的 game_code, game_name, oid, game_option_list_type, room_id（如有）

    Args:
        response (dict): 從 API 拿到的完整 response

    Returns:
        tuple: (錯誤碼: int, game_type_map: dict[str, set[str]], game_data_list: list[dict])
    """
    try:
        game_list_order = extract_nested(response, "data.game_list_order", {})
        game_option_list = extract_nested(response, "data.game_option_list", [])

        if not game_list_order or not game_option_list:
            return ResultCode.TASK_GAME_LIST_STRUCTURE_INVALID, {}, []

        game_type_map = {
            "type_1": set(game_list_order.get("sorted_arcade_game_list", [])),
            "type_2": set(game_list_order.get("sorted_slot_game_list", [])),
            "type_3": set(game_list_order.get("sorted_table_game_list", [])),
            "type_4": set(game_list_order.get("sorted_bingo_game_list", [])),
        }

        game_data_list = []
        for game in game_option_list:
            game_code = game.get("game_code")
            game_name = game.get("game_name")
            game_type = int(game.get("game_type", -1))
            option_list = game.get("game_option", [])

            for option in option_list:
                oid = option.get("oid")
                other_info_str = option.get("other_info", "")
                room_id = None

                if game_type == 3 and other_info_str:
                    try:
                        other_info = json.loads(other_info_str)
                        room_id = other_info.get("room_no")
                    except Exception:
                        room_id = None

                if game_code and game_name and oid:
                    game_data_list.append({
                        "game_code": game_code,
                        "game_name": game_name,
                        "oid": str(oid),
                        "game_option_list_type": game_type,
                        "room_id": room_id,
                    })

        return ResultCode.SUCCESS, game_type_map, game_data_list

    except Exception:
        return ResultCode.TASK_EXCEPTION, {}, []
