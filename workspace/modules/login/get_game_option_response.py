"""
🎯 任務模組：取得遊戲列表完整 response 結構
"""

from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_GAME_LIST_PATH
from workspace.tools.token.token_login_cache import load_login_token
from workspace.tools.network.request_handler import safe_get
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode


def fetch_game_option_response(account: str) -> dict | int:
    """
    根據帳號呼叫遊戲列表 API，取得完整 response dict

    Args:
        account (str): 玩家帳號（對應登入 token 快取檔）

    Returns:
        dict | int: 成功回傳 response dict，失敗回傳錯誤碼
    """
    print_info(f"📡 正在請求遊戲列表資料 for account = {account}")

    url = f"{R88_API_BASE_URL}{R88_GAME_LIST_PATH}"
    token = load_login_token(account)
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = safe_get(url, headers=headers)
        return response.json()
    except Exception as e:
        print_error(f"❌ API 請求或解析失敗：{e}")
        return ResultCode.TASK_API_FAILED


if __name__ == "__main__":
    result = fetch_game_option_response("qa0002")
    print(result)
