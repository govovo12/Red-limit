import json
from pathlib import Path

_CACHE_PATH = Path(".cache")


def save_login_token(account: str, token: str) -> None:
    """
    儲存帳號登入 token 至 .cache/token_login_<account>.json
    """
    _CACHE_PATH.mkdir(parents=True, exist_ok=True)
    cache_file = _CACHE_PATH / f"token_login_{account}.json"
    with cache_file.open("w", encoding="utf-8") as f:
        json.dump(
            {"account": account, "token": token},
            f,
            ensure_ascii=False,
            indent=2
        )


def load_login_token(account: str) -> str | None:
    """
    從快取中讀取帳號登入 token
    """
    cache_file = _CACHE_PATH / f"token_login_{account}.json"
    if not cache_file.exists():
        return None
    with cache_file.open(encoding="utf-8") as f:
        return json.load(f).get("token")
