import json
from datetime import datetime, timedelta
from typing import Optional, Tuple

from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.decorator import tool
from workspace.config.paths import get_auth_token_cache_path  # ✅ 加這行

_EXPIRE_MINUTES = 10

@tool
def load_token() -> Tuple[int, Optional[str]]:
    """
    嘗試從快取中載入 token。若過期或不存在則回傳錯誤碼。

    :return: (錯誤碼, token字串 or None)
    """
    cache_path = get_auth_token_cache_path()  # ✅ 改這裡

    if not cache_path.exists():
        return ResultCode.TOOL_TOKEN_NOT_FOUND, None

    try:
        with cache_path.open("r", encoding="utf-8") as f:
            content = json.load(f)
    except Exception:
        return ResultCode.TOOL_TOKEN_LOAD_FAILED, None

    token = content.get("token")
    expire_at = content.get("expire_at")

    if not token or not expire_at:
        return ResultCode.TOOL_TOKEN_MISSING_FIELD, None

    try:
        expire_time = datetime.fromisoformat(expire_at)
    except ValueError:
        return ResultCode.TOOL_TOKEN_TIME_PARSE_FAILED, None

    if datetime.utcnow() > expire_time:
        return ResultCode.TOOL_TOKEN_EXPIRED, None

    return ResultCode.SUCCESS, token


@tool
def save_token(token: str) -> int:
    """
    儲存 token 並寫入過期時間。

    :param token: JWT token 字串
    :return: 錯誤碼
    """
    cache_path = get_auth_token_cache_path()  # ✅ 改這裡
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "token": token,
        "expire_at": (datetime.utcnow() + timedelta(minutes=_EXPIRE_MINUTES)).isoformat()
    }

    try:
        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TOOL_TOKEN_SAVE_FAILED
