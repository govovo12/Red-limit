from workspace.tools.common.result_code import ResultCode
from workspace.tools.file.data_loader import save_json
from workspace.config.paths import get_oid_by_type_path


def save_oid_map_to_cache(oid_map: dict) -> int:
    """
    將分類後的 OID 結果寫入快取檔案（.cache/oid_by_type.json）。

    Args:
        oid_map (dict): 類型對應 OID 結果，如 { "type_1": [{oid, game_name}], ... }

    Returns:
        int: 錯誤碼（成功為 ResultCode.SUCCESS）
    """
    try:
        error_code, ok = save_json(oid_map, get_oid_by_type_path())
        if not ok:
            return error_code

        return ResultCode.SUCCESS

    except Exception:
        return ResultCode.TASK_EXCEPTION
