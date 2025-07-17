# workspace/modules/batch/generate_all_type_tasks.py

from workspace.config.paths import get_oid_list_path
from workspace.tools.file.data_loader import load_json
from workspace.modules.batch.generate_account_oid_pairs import generate_account_oid_pairs
from workspace.tools.common.result_code import ResultCode


def generate_all_type_tasks() -> dict:
    """
    一次產生所有 type 的任務清單，帳號由單一產生器全域分配，保證不重複。
    預設依照 TYPE_ORDER 中的順序分配帳號（type1 → type2 → type3 ...）
    """
    # 📥 讀取快取中所有 type 對應的 oid/game 資料
    path = get_oid_list_path()
    code, data = load_json(path)

    if code != ResultCode.SUCCESS or not isinstance(data, dict):
        return {}

    # 📌 指定帳號分配順序（若未來有更多 type，請補在這裡）
    TYPE_ORDER = ["type_1", "type_2", "type_3", "type_4"]

    # 🧮 扁平化所有 OID 清單（確保帳號產生足夠數量）
    all_oid_list = [game for type_key in TYPE_ORDER if type_key in data for game in data[type_key]]
    result_list, code = generate_account_oid_pairs(all_oid_list)

    if code != ResultCode.SUCCESS:
        return {}

    # 🏗️ 依指定順序將帳號填入對應 type 清單
    final_result = {}
    current_index = 0

    for type_key in TYPE_ORDER:
        if type_key not in data:
            continue

        game_list = data[type_key]
        enriched = []
        for i in range(len(game_list)):
            task = result_list[current_index]
            current_index += 1
            enriched.append(task)
        final_result[type_key] = enriched

    return final_result
