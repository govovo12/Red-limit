from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_GAME_LIST_PATH
from workspace.tools.token.token_login_cache import load_login_token
from workspace.tools.network.request_handler import safe_get
from workspace.tools.common.result_code import ResultCode


def fetch_game_option_response(account: str) -> dict | int:
    """
    任務模組：根據帳號呼叫遊戲列表 API，取得完整 response dict。

    Args:
        account (str): 玩家帳號（對應登入 token 快取檔）

    Returns:
        dict | int: 成功回傳 response dict，失敗回傳錯誤碼
    """
    try:
        token = load_login_token(account)
        if not token:
            return ResultCode.TASK_LOGIN_TOKEN_NOT_FOUND

        url = f"{R88_API_BASE_URL}{R88_GAME_LIST_PATH}"
        headers = {"Authorization": f"Bearer {token}"}

        response = safe_get(url, headers=headers)
        if not response or not response.ok:
            return ResultCode.TASK_GAME_LIST_API_FAILED

        return response.json()

    except Exception:
        return ResultCode.TASK_EXCEPTION
