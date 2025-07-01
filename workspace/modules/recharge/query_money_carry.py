"""
任務模組：查詢帳號餘額，用於 money_carry 判斷
"""

# 🔧 錯誤碼與路徑
from workspace.tools.common.result_code import ResultCode
from workspace.config.paths import get_api_key_path

# 📦 請求與 JSON 工具
from workspace.tools.network.request_handler import get
from workspace.tools.network.response_helper import extract_nested
from workspace.tools.file.data_loader import load_json

# ⚙️ 環境設定
from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_BALANCE_PATH


def query_money_carry(account: str) -> tuple[int, float | None]:
    """
    查詢指定帳號的錢包餘額。
    若查詢成功，回傳 (ResultCode.SUCCESS, 金額)
    若失敗，回傳 (錯誤碼, None)
    """
    try:
        code, api_info = load_json(get_api_key_path())
        if code != ResultCode.SUCCESS:
            return code, None

        pf_id = api_info.get("pf_id")
        api_key = api_info.get("api_key")
        if not pf_id or not api_key:
            return ResultCode.TASK_RECHARGE_MISSING_KEY, None

        headers = {
            "pf_id": pf_id,
            "timestamp": "0",
            "api_key": api_key
        }

        url = f"{R88_API_BASE_URL.rstrip('/')}{R88_BALANCE_PATH}/{account}"
        code, response = get(url, headers=headers)

        print(f"[DEBUG] 查餘額回應：code={code}, raw={response}")

        if code != 0:
            return ResultCode.TASK_RECHARGE_EXCEPTION, None

        json_data = response.json()
        print(f"[DEBUG] 查餘額 JSON：{json_data}")

        if json_data.get("code") != 0:
            return ResultCode.TASK_RECHARGE_API_FAILED, None

        balance = extract_nested(json_data, "data.balance", default=None)
        print(f"[DEBUG] balance 採集結果：{balance}")

        if balance is None:
            return ResultCode.TASK_RECHARGE_MISSING_BALANCE, None

        return ResultCode.SUCCESS, float(balance)

    except Exception as e:
        print(f"[DEBUG] 查餘額發生例外：{e}")
        return ResultCode.TASK_RECHARGE_EXCEPTION, None
