import json
from pathlib import Path
from typing import Optional

from workspace.tools.common.decorator import tool


_CACHE_PATH = Path(".cache")


@tool
def save_lobby_token(account: str, token: str) -> None:
    """
    儲存大廳 token 至快取檔案中

    Args:
        account (str): 呼叫該 token 的帳號
        token (str): 拿到的大廳 token 字串
    """
    cache_file = _CACHE_PATH / f"token_lobby_{account}.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    with cache_file.open("w", encoding="utf-8") as f:
        json.dump({"account": account, "token": token}, f, ensure_ascii=False, indent=2)


def load_lobby_token(account: str) -> Optional[str]:
    """
    從快取中讀取指定帳號的大廳 token
    """
    cache_file = _CACHE_PATH / f"token_lobby_{account}.json"
    if not cache_file.exists():
        return None
    with cache_file.open(encoding="utf-8") as f:
        return json.load(f).get("token")
