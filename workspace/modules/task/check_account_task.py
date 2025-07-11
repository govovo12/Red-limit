from workspace.tools.network.request_handler import safe_get
from workspace.tools.network.response_helper import extract_nested
from workspace.tools.common.result_code import ResultCode
from workspace.config.paths import get_api_key_path
from workspace.tools.file.data_loader import load_json
from workspace.tools.env.config_loader import PF_ID, get_check_account_url

async def check_account_exists(account: str) -> tuple[int, str | None]:
    """
    發送 API 確認此帳號是否已與 pf_id 建立對應關係。
    回傳 (錯誤碼, pf_account)，若查無對應則 pf_account 為 None。
    """
    # Step 1: 取得 api_key
    code, api_data = load_json(get_api_key_path())
    if code != ResultCode.SUCCESS or not api_data:
        return ResultCode.TASK_API_KEY_MISSING, None

    api_key = api_data.get("api_key")
    if not api_key:
        return ResultCode.TASK_API_KEY_MISSING, None

    # Step 2: 組 headers 與 URL
    headers = {
        "pf_id": PF_ID,
        "timestamp": "0",
        "api_key": api_key,
    }

    url = get_check_account_url(account)

    # Step 3: 發送 GET 請求
    try:
        response = safe_get(url, headers=headers)
        res_json = response.json()

        # Step 4: 擷取 pf_account
        pf_account = extract_nested(res_json, "data.pf_account")
        if not pf_account:
            return ResultCode.TASK_ACCOUNT_NOT_LINKED, None

        return ResultCode.SUCCESS, pf_account

    except Exception:
        return ResultCode.TASK_CHECK_ACCOUNT_FAILED, None
