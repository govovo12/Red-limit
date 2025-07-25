import re
from workspace.tools.common.result_code import ResultCode


def validate_pf_id(pf_id: str) -> tuple[str | None, int]:
    if "_" not in pf_id:
        return None, ResultCode.TASK_INVALID_PFID
    if not re.fullmatch(r"[a-zA-Z0-9_]+", pf_id):
        return None, ResultCode.TASK_INVALID_PFID
    return pf_id, ResultCode.SUCCESS


def validate_private_key(key: str) -> tuple[str | None, int]:
    key = key.strip()
    if not re.fullmatch(r"[a-zA-Z0-9]{32}", key):
        return None, ResultCode.TASK_INVALID_PRIVATE_KEY
    return key, ResultCode.SUCCESS
