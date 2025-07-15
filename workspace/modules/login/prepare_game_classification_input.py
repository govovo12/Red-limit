import json
from collections import defaultdict
from workspace.tools.network.response_helper import extract_nested
from workspace.tools.common.result_code import ResultCode


def prepare_game_classification_input(response: dict) -> tuple[int, dict]:
    """
    從 /get_game_list 回傳擷取每款遊戲的 oid / game_name / room_id，
    並依 game_type 整理為 type_1 ~ type_N 分類格式。

    Returns:
        (錯誤碼: int, 分類後的遊戲 dict)
    """
    try:
        game_option_list = extract_nested(response, "data.game_option_list", [])
        if not game_option_list:
            return ResultCode.TASK_GAME_LIST_STRUCTURE_INVALID, {}

        result_by_type = defaultdict(list)

        for game in game_option_list:
            game_code = game.get("game_code", "")
            if game_code.startswith("Turbo"):
                continue  # ✅ 篩掉 Turbo 系列

            game_name = game.get("game_name", "")
            game_type_raw = game.get("game_type", "")
            game_type_key = f"type_{game_type_raw}"

            option_list = game.get("game_option", [])
            for option in option_list:
                oid = option.get("oid")
                other_info_str = option.get("other_info", "")
                room_id = None

                if other_info_str:
                    try:
                        other_info = json.loads(other_info_str)
                        room_id = other_info.get("room_no")
                    except Exception:
                        room_id = None

                if oid and game_name:
                    result_by_type[game_type_key].append({
                        "oid": str(oid),
                        "game_name": game_name,
                        "room_id": room_id
                    })

        return ResultCode.SUCCESS, dict(result_by_type)

    except Exception:
        return ResultCode.TASK_EXCEPTION, {}
