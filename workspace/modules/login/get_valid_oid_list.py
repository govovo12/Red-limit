"""
從遊戲列表 response 中擷取所有 OID，依據 game_type 分類回傳。
每個 type 對應一個 list，list 中每筆包含 oid 與 game_name。
並支援錯誤碼與筆數統計印出。
"""

# ===== 🔧 錯誤碼與路徑 =====
from workspace.tools.common.result_code import ResultCode

# ===== 🔧 工具模組 =====
from workspace.tools.network.response_helper import extract_nested
from workspace.tools.printer.printer import print_info, print_error


def get_valid_oid_list_from_response(response: dict) -> dict | int:
    """
    從 response 中擷取遊戲 OID，並依 game_type 分類。

    回傳格式範例：
    {
        "type_2": [
            {"oid": "301", "game_name": "水果機"},
            {"oid": "302", "game_name": "水果機"}
        ],
        "type_1": [
            {"oid": "101", "game_name": "骰子賽"}
        ]
    }
    若 response 結構異常，回傳錯誤碼。
    """
    result = {}
    game_list = extract_nested(response, "data.game_option_list", default=[])

    if not isinstance(game_list, list):
        print_error("❌ 找不到有效的 game_option_list，無法提取 OID")
        return ResultCode.TASK_EMPTY_GAME_LIST

    for game in game_list:
        game_type = extract_nested(game, "game_type")
        game_name = extract_nested(game, "game_name", default="未知遊戲")
        options = extract_nested(game, "game_option", default=[])

        if not game_type:
            continue

        key = f"type_{game_type}"
        if key not in result:
            result[key] = []

        for opt in options:
            oid = extract_nested(opt, "oid")
            if not oid:
                continue
            result[key].append({
                "oid": str(oid),
                "game_name": game_name
            })

    if not result:
        print_error("❌ OID 擷取失敗，無任何有效資料")
        return ResultCode.TASK_EMPTY_OID_LIST

    # 印出各類型 OID 統計
    print_info("📦 成功擷取 OID 並分類：")
    for type_key, group in result.items():
        print_info(f"- {type_key}：{len(group)} 筆")

    return result
