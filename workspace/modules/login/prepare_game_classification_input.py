from workspace.tools.network.response_helper import extract_nested
import json  # ✅ 新增：用來解析 other_info


def prepare_game_classification_input(response: dict) -> tuple[dict, list]:
    """
    將 /get_game_list 的原始 response 拆解成：
    - game_type_map: 各分類對應的 game_code 清單
    - game_data_list: 每筆遊戲對應的 game_code, game_name, oid, game_option_list_type, room_id（如有）

    Args:
        response (dict): 從 API 拿到的完整 response

    Returns:
        tuple: (game_type_map: dict[str, set[str]], game_data_list: list[dict])
    """
    # 提取巢狀結構
    game_list_order = extract_nested(response, "data.game_list_order", {})
    game_option_list = extract_nested(response, "data.game_option_list", [])

    # 建立 type ➜ set of game_code 對應表
    game_type_map = {
        "type_1": set(game_list_order.get("sorted_arcade_game_list", [])),
        "type_2": set(game_list_order.get("sorted_slot_game_list", [])),
        "type_3": set(game_list_order.get("sorted_table_game_list", [])),
        "type_4": set(game_list_order.get("sorted_bingo_game_list", [])),
    }

    # 建立所有遊戲資料（展平 game_option list）
    game_data_list = []
    for game in game_option_list:
        game_code = game.get("game_code")
        game_name = game.get("game_name")
        game_type = int(game.get("game_type", -1))  # ✅ 強制型別，避免寫出 str
        option_list = game.get("game_option", [])

        for option in option_list:
            oid = option.get("oid")
            other_info_str = option.get("other_info", "")

            # ✅ 新增區塊：僅在 type 3 遊戲解析 room_id
            room_id = None
            if game_type == 3 and other_info_str:
                try:
                    other_info = json.loads(other_info_str)
                    room_id = other_info.get("room_no")
                except Exception:
                    room_id = None  # 安全 fallback

            if game_code and game_name and oid:
                game_data_list.append({
                    "game_code": game_code,
                    "game_name": game_name,
                    "oid": str(oid),
                    "game_option_list_type": game_type,
                    "room_id": room_id  # ✅ 新增欄位（type 3 才會有值）
                })

    return game_type_map, game_data_list
