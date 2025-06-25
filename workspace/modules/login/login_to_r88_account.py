"""
任務模組：使用大廳 token 登入 R88，取得帳號 access_token 並快取
"""

from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_ACCOUNT_LOGIN_PATH
from workspace.tools.network.request_handler import safe_post
from workspace.tools.token.token_lobby_cache import load_lobby_token
from workspace.tools.token.token_login_cache import save_login_token
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode

def login_to_r88_account(account: str) -> int:
    try:
        lobby_token = load_lobby_token(account)
        if not lobby_token:
            raise RuntimeError(f"未找到帳號 {account} 的大廳 token 快取")

        url = f"{R88_API_BASE_URL}{R88_ACCOUNT_LOGIN_PATH}"
        headers = {"Content-Type": "application/json"}
        payload = {"token": lobby_token}

        print_info(f"🔐 正在登入帳號 {account}...")
        rs = safe_post(url, headers=headers, json=payload)
        response_data = rs.json()

        print_info(f"🧾 API 回傳：{response_data}")

        data = response_data.get("data", {})
        access_token = data.get("access_token") or data.get("access_token ")

        if not access_token:
            raise RuntimeError("API 回傳中未取得 access_token（含容錯）")

        save_login_token(account, access_token)
        print_info(f"✅ 帳號 {account} 的登入 token 快取成功：{access_token}")
        return ResultCode.SUCCESS

    except Exception as e:
        print_error(f"❌ 任務模組執行失敗：{e}")
        return ResultCode.TASK_LOGIN_TO_ACCOUNT_FAILED

if __name__ == "__main__":
    login_to_r88_account("qa0002")
