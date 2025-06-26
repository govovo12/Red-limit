"""
任務模組：使用 lobby_token 取得 access_token，並將結果加入原始 task dict
"""

from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_ACCOUNT_LOGIN_PATH
from workspace.tools.network.request_handler import safe_post
from workspace.tools.common.result_code import ResultCode

def get_access_token_task(task: dict) -> tuple[dict, int]:
    """
    使用 task 中的 lobby_token 取得 access_token，並附加在 task dict 中返回。
    回傳 (task, ResultCode)
    """
    account = task.get("account")
    lobby_token = task.get("lobby_token")

    if not lobby_token:
        # 不 raise，避免中斷流程，只當成失敗處理
        task["access_token"] = None
        return task, ResultCode.TASK_LOGIN_TO_ACCOUNT_FAILED

    try:
        url = f"{R88_API_BASE_URL}{R88_ACCOUNT_LOGIN_PATH}"
        headers = {"Content-Type": "application/json"}
        payload = {"token": lobby_token}

        rs = safe_post(url, headers=headers, json=payload)
        response_data = rs.json()

        data = response_data.get("data", {})
        access_token = data.get("access_token") or data.get("access_token ")

        if not access_token:
            task["access_token"] = None
            return task, ResultCode.TASK_LOGIN_TO_ACCOUNT_FAILED

        task["access_token"] = access_token
        return task, ResultCode.SUCCESS

    except Exception:
        task["access_token"] = None
        return task, ResultCode.TASK_LOGIN_TO_ACCOUNT_FAILED
