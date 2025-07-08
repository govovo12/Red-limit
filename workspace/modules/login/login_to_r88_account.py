from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_ACCOUNT_LOGIN_PATH
from workspace.tools.network.request_handler import safe_post
from workspace.tools.token.token_lobby_cache import load_lobby_token
from workspace.tools.token.token_login_cache import save_login_token
from workspace.tools.common.result_code import ResultCode


def login_to_r88_account(account: str) -> int:
    """
    任務模組：使用大廳 token 登入 R88，取得帳號 access_token 並快取。

    Args:
        account (str): 帳號名稱

    Returns:
        int: 錯誤碼（成功為 ResultCode.SUCCESS）
    """
    try:
        lobby_token = load_lobby_token(account)
        if not lobby_token:
            return ResultCode.TASK_LOBBY_TOKEN_NOT_FOUND

        url = f"{R88_API_BASE_URL}{R88_ACCOUNT_LOGIN_PATH}"
        headers = {"Content-Type": "application/json"}
        payload = {"token": lobby_token}

        rs = safe_post(url, headers=headers, json=payload)
        if not rs or not rs.ok:
            return ResultCode.TASK_ACCOUNT_LOGIN_API_FAILED

        response_data = rs.json()
        data = response_data.get("data", {})
        access_token = data.get("access_token") or data.get("access_token ")

        if not access_token:
            return ResultCode.TASK_ACCESS_TOKEN_MISSING

        save_login_token(account, access_token)
        return ResultCode.SUCCESS

    except Exception:
        return ResultCode.TASK_EXCEPTION
