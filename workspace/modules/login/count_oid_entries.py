from workspace.tools.common.result_code import ResultCode


def count_oid_entries(oid_map: dict) -> tuple[int, dict[str, int]]:
    """
    任務模組：統計各類型 OID 筆數與總筆數。

    Args:
        oid_map (dict): 分類結果，如 { "type_1": [{...}], ... }

    Returns:
        tuple: (錯誤碼, 統計結果 dict，如 {"type_1": 34, ..., "total": 115})
    """
    try:
        if not isinstance(oid_map, dict):
            return ResultCode.TASK_OID_MAP_INVALID, {}

        type_counts = {k: len(v) for k, v in oid_map.items()}
        total_count = sum(type_counts.values())
        type_counts["total"] = total_count

        return ResultCode.SUCCESS, type_counts

    except Exception:
        return ResultCode.TASK_EXCEPTION, {}
