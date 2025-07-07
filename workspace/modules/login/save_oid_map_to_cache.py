from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode
from workspace.tools.file.data_loader import save_json
from workspace.config.paths import get_oid_by_type_path


def save_oid_map_to_cache(oid_map: dict) -> int:
    """
    將分類後的 OID 結果寫入快取檔案（.cache/oid_by_type.json），並印出統計資訊。

    Args:
        oid_map (dict): 類型對應 OID 結果，如 { "type_1": [{oid, game_name}], ... }

    Returns:
        int: 錯誤碼（成功為 ResultCode.SUCCESS）
    """
    # 統計數量
    oid_count = sum(len(group) for group in oid_map.values())
    print_info(f"✅ 擷取成功，總共 {oid_count} 筆 OID")
    for type_key, group in oid_map.items():
        print_info(f"- {type_key}：{len(group)} 筆")

    # 儲存至快取
    error_code, ok = save_json(oid_map, get_oid_by_type_path())
    if not ok:
        print_error("❌ 寫入 OID 快取失敗")
        return error_code

    print_info(f"📁 OID 快取已寫入：{get_oid_by_type_path()}")
    return ResultCode.SUCCESS
