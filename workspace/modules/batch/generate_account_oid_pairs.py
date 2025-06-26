# workspace/modules/batch/generate_account_oid_pairs.py

"""
任務模組：generate_account_oid_pairs

根據 OID + game_name 清單，自動產生對應帳號（qa0001 ~ qaNN），
並組成包含 account/oid/game_name 的 dict 清單，供後續流程使用。
"""

# ===== 匯入區塊 =====
from typing import List
from workspace.tools.printer.printer import print_info


def generate_account_oid_pairs(oid_info_list: List[dict], prefix: str = "qa") -> List[dict]:
    """
    根據 OID 清單自動產生對應帳號，並組成完整任務物件（dict）。

    :param oid_info_list: 每筆包含 "oid" 與 "game_name" 的 dict 清單
    :param prefix: 帳號前綴，預設為 "qa"
    :return: List of {"account", "oid", "game_name"}
    """
    if not oid_info_list:
        print_info("[generate_account_oid_pairs] ⚠️ OID 清單為空，無法配對帳號")
        return []

    result = []
    for index, entry in enumerate(oid_info_list, start=1):
        task = dict(entry)  # 複製原始欄位
        task["account"] = f"{prefix}{index:04d}"
        result.append(task)

    print_info(f"[generate_account_oid_pairs] ✅ 完成帳號配對，共 {len(result)} 組")
    return result