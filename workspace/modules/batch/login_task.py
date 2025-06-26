# workspace/modules/batch/login_task.py

"""
任務模組：login_task

每條執行緒接收一筆 task dict，根據 account 執行登入 API，
並將取得的 token 寫入 task["lobby_token"]。
"""

from workspace.tools.network.request_handler import safe_post
from workspace.tools.file.data_loader import load_json
from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_LOBBY_LOGIN_PATH
from workspace.tools.printer.printer import print_error
from workspace.tools.common.result_code import ResultCode

def run_login_task(task: dict) -> int:
    """
    多線任務：登入並將 token 寫入 task dict。
    :param task: 包含 account, oid, game_name 的 dict
    :return: 錯誤碼
    """
    account = task["account"]

    try:
        url = f"{R88_API_BASE_URL}{R88_LOBBY_LOGIN_PATH}"

        code, result = load_json(path=".cache/api_key.json")
        if code != ResultCode.SUCCESS or not isinstance(result, dict):
            print_error(f"[{account}] 無法讀取 API 金鑰")
            return ResultCode.TASK_GET_LOBBY_TOKEN_FAILED

        headers = {
            "api_key": result.get("api_key"),
            "pf_id": result.get("pf_id"),
            "timestamp": "0"
        }
        payload = {"account": account}

        response = safe_post(url=url, headers=headers, json=payload)
        full_url = response.json().get("data", {}).get("url")

        if not full_url or "?" not in full_url:
            print_error(f"[{account}] ⚠️ 回傳中找不到 token URL")
            return ResultCode.TASK_GET_LOBBY_TOKEN_FAILED

        token = full_url.split("?")[-1]
        if not token:
            print_error(f"[{account}] ⚠️ token 擷取失敗")
            return ResultCode.TASK_GET_LOBBY_TOKEN_FAILED

        task["lobby_token"] = token
        return ResultCode.SUCCESS

    except Exception as e:
        print_error(f"[{account}] ❌ 任務錯誤：{e}")
        return ResultCode.TASK_GET_LOBBY_TOKEN_FAILED
