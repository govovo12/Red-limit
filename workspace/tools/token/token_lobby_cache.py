import json
from typing import Optional
from workspace.tools.common.decorator import tool
from workspace.config.paths import get_token_lobby_cache_file  # ✅ 改這行

@tool
def save_lobby_token(account: str, token: str) -> None:
    cache_file = get_token_lobby_cache_file(account)  # ✅ 改這裡
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    with cache_file.open("w", encoding="utf-8") as f:
        json.dump({"account": account, "token": token}, f, ensure_ascii=False, indent=2)

def load_lobby_token(account: str) -> Optional[str]:
    cache_file = get_token_lobby_cache_file(account)  # ✅ 改這裡
    if not cache_file.exists():
        return None
    with cache_file.open(encoding="utf-8") as f:
        return json.load(f).get("token")
