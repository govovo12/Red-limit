import json
from pathlib import Path

from workspace.tools.env.config_loader import PF_ID, PRIVATE_KEY
from workspace.tools.token.token_generator import generate_api_key
from workspace.tools.common.result_code import ResultCode
from workspace.init_env import setup


setup()

_CACHE_PATH = Path(".cache/api_key.json")


def generate_r88_api_key() -> int:
    """
    任務模組：產生 R88 前台登入用的 API Key 並快取至 .cache。

    Returns:
        int: 錯誤碼（成功為 ResultCode.SUCCESS）
    """
    try:
        api_key = generate_api_key(PF_ID, PRIVATE_KEY)
    except Exception:
        return ResultCode.TASK_API_KEY_GENERATION_FAILED

    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _CACHE_PATH.open("w", encoding="utf-8") as f:
            json.dump({
                "pf_id": PF_ID,
                "api_key": api_key
            }, f, ensure_ascii=False, indent=2)
    except Exception:
        return ResultCode.TASK_API_KEY_CACHE_FAILED

    return ResultCode.SUCCESS
