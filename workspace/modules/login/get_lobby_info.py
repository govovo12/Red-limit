from pathlib import Path

from workspace.tools.network.request_handler import safe_post
from workspace.tools.token.token_lobby_cache import save_lobby_token
from workspace.tools.file.data_loader import load_json
from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_LOBBY_LOGIN_PATH
from workspace.tools.common.result_code import ResultCode


def get_lobby_token(account: str) -> int:
    """
    任務模組：呼叫 login API 發送請求，取得大廳 token 並快取。

    Args:
        account (str): 登入帳號

    Returns:
        int: 錯誤碼（成功為 ResultCode.SUCCESS）
    """
    try:
        url = f"{R88_API_BASE_URL}{R88_LOBBY_LOGIN_PATH}"

        # Step 1: 載入 API 金鑰
        code, result = load_json(Path(".cache/api_key.json"))
        if code != ResultCode.SUCCESS or not isinstance(result, dict):
            return ResultCode.TASK_API_KEY_LOAD_FAILED

        headers = {
            "api_key": result.get("api_key"),
            "pf_id": result.get("pf_id"),
            "timestamp": "0"
        }
        payload = {"account": account}

        # Step 2: 發送登入請求
        response = safe_post(url=url, headers=headers, json=payload)
        if not response or not response.ok:
            return ResultCode.TASK_LOBBY_API_REQUEST_FAILED

        # Step 3: 擷取 token 並快取
        full_url = response.json().get("data", {}).get("url")
        if not full_url or "?" not in full_url:
            return ResultCode.TASK_LOBBY_URL_MISSING

        token = full_url.split("?")[-1]
        if not token:
            return ResultCode.TASK_LOBBY_TOKEN_EXTRACTION_FAILED

        save_lobby_token(account, token)
        return ResultCode.SUCCESS

    except Exception:
        return ResultCode.TASK_EXCEPTION
