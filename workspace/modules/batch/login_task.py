# workspace/modules/batch/login_task.py

from workspace.tools.network.request_handler import safe_post
from workspace.tools.file.data_loader import load_json
from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_LOBBY_LOGIN_PATH
from workspace.tools.common.result_code import ResultCode


def run_login_task(task: dict) -> int:
    """
    多線任務：登入並將 token 寫入 task dict。
    :param task: 包含 account, oid, game_name 的 dict
    :return: 錯誤碼
    """
    account = task.get("account")

    try:
        url = f"{R88_API_BASE_URL}{R88_LOBBY_LOGIN_PATH}"
        code, result = load_json(path=".cache/api_key.json")
        if code != ResultCode.SUCCESS or not isinstance(result, dict):
            return ResultCode.TASK_LOBBY_API_KEY_LOAD_FAILED

        headers = {
            "api_key": result.get("api_key"),
            "pf_id": result.get("pf_id"),
            "timestamp": "0"
        }
        payload = {"account": account}

        response = safe_post(url=url, headers=headers, json=payload)
        full_url = response.json().get("data", {}).get("url")

        if not full_url or "?" not in full_url:
            return ResultCode.TASK_LOBBY_TOKEN_EXTRACTION_FAILED

        token = full_url.split("?")[-1]
        if not token:
            return ResultCode.TASK_LOBBY_TOKEN_EXTRACTION_FAILED

        task["lobby_token"] = token
        return ResultCode.SUCCESS

    except Exception:
        return ResultCode.TASK_GET_LOBBY_TOKEN_FAILED
