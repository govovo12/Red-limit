# workspace/modules/batch/prepare_oid_list_by_type.py

"""
任務模組：prepare_oid_list_by_type

根據 game_type 從快取中取得 OID 清單。
支援傳入 ALL 回傳所有類型，並保持 dict[type] = list 格式。
"""

from typing import Tuple, List, Dict
from workspace.tools.file.data_loader import load_json
from workspace.config.paths import get_oid_by_type_path
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info


def get_oid_list_by_type(game_type: str) -> Tuple[int, List[dict] | Dict[str, List[dict]]]:
    """
    根據指定類型取得 OID 清單。
    - 若為單一類型，回傳 List[dict]，每筆附上 "type"
    - 若為 "ALL"，回傳 Dict[type] = List[dict]，每筆亦含 "type"
    :param game_type: "type_1", "type_2", "type_3" 或 "ALL"
    :return: (錯誤碼, 清單或分類 dict)
    """
    code, data = load_json(get_oid_by_type_path())
    print_info(f"[DEBUG] 讀到的快取 key 有：{list(data.keys())}")
    if code != ResultCode.SUCCESS or not isinstance(data, dict):
        return code, []

    if game_type == "ALL":
        result = {}
        for type_key, entries in data.items():
            result[type_key] = []
            for entry in entries:
                result[type_key].append({
                    "oid": str(entry["oid"]),
                    "game_name": entry["game_name"],
                    "type": type_key
                })
        return ResultCode.SUCCESS, result

    if game_type not in data:
        return ResultCode.TASK_TYPE_NOT_FOUND, []

    result = []
    for entry in data[game_type]:
        result.append({
            "oid": str(entry["oid"]),
            "game_name": entry["game_name"],
            "type": game_type
        })
    return ResultCode.SUCCESS, result
