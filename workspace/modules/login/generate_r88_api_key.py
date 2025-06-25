import json
from pathlib import Path

from workspace.tools.env.config_loader import PF_ID, PRIVATE_KEY
from workspace.tools.token.token_generator import generate_api_key
from workspace.tools.printer.printer import print_info
from workspace.tools.common.decorator import task
from workspace.init_env import setup
setup()

_CACHE_PATH = Path(".cache/api_key.json")


def generate_r88_api_key() -> str:
    """
    任務模組：產生 R88 前台登入用的 API Key，並印出與快取。

    Returns:
        str: 計算後的 API Key 字串
    """
    api_key = generate_api_key(PF_ID, PRIVATE_KEY)

    print_info(f"✅ 產生的 API Key：{api_key}")

    # 儲存到 .cache/api_key.json
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump({
            "pf_id": PF_ID,
            "api_key": api_key
        }, f, ensure_ascii=False, indent=2)

    print_info(f"📁 API Key 已快取至：{_CACHE_PATH}")
    return api_key


if __name__ == "__main__":
    generate_r88_api_key()
