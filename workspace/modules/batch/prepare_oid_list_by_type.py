from workspace.config.paths import get_oid_by_type_path
from workspace.tools.file.data_loader import load_json
from workspace.tools.common.result_code import ResultCode

def get_oid_list_by_type(game_type: str):
    """
    根據指定的 game_type，從快取中讀取對應的 OID 清單。
    - 若 game_type 為 "ALL"，會回傳所有 type 對應的清單（含各自 count）。
    - 若指定單一 type，則包成一個 dict，含 type, count, data。

    Returns:
        (int, dict): ResultCode, Dict
    """
    path = get_oid_by_type_path()
    code, data = load_json(path)

    if code != ResultCode.SUCCESS:
        return code, {}

    if not data or (game_type != "ALL" and game_type not in data):
        return ResultCode.TASK_OID_LIST_FOR_TYPE_NOT_FOUND, {}

    if game_type == "ALL":
        result_by_type = {}
        for type_key, entries in data.items():
            for entry in entries:
                entry["oid"] = str(entry["oid"])  # 確保 oid 是字串
            result_by_type[type_key] = {
                "type": type_key,
                "count": len(entries),
                "data": {type_key: entries}
            }
        return ResultCode.SUCCESS, result_by_type

    else:
        entries = data[game_type]
        for entry in entries:
            entry["oid"] = str(entry["oid"])  # 確保 oid 是字串

        return ResultCode.SUCCESS, {
            "type": game_type,
            "count": len(entries),
            "data": {game_type: entries}
        }
