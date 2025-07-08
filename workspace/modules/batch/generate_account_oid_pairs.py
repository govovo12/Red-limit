# workspace/modules/batch/generate_account_oid_pairs.py

from typing import List, Tuple
from workspace.tools.common.result_code import ResultCode

def generate_account_oid_pairs(oid_info_list: List[dict], prefix: str = "qa") -> Tuple[List[dict], int]:
    """
    根據 OID 清單自動產生對應帳號，並組成完整任務物件（dict）。

    :param oid_info_list: 每筆包含 "oid" 與 "game_name" 的 dict 清單
    :param prefix: 帳號前綴，預設為 "qa"
    :return: (result list, result code)
    """
    if not oid_info_list:
        return [], ResultCode.TASK_ACCOUNT_PAIRING_EMPTY_INPUT

    result = []
    for index, entry in enumerate(oid_info_list, start=1):
        task = dict(entry)  # 複製原始欄位
        task["account"] = f"{prefix}{index:04d}"
        result.append(task)

    return result, ResultCode.SUCCESS
