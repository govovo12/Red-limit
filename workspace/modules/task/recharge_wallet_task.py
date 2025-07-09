"""
任務模組（async）：錢包加值

根據下注金額規則自動加值最低金額給指定帳號，透過新版平台轉帳 API 發送請求。
"""

# === 標準工具 ===
import time
from uuid import uuid4

# === 錯誤碼與路徑 ===
from workspace.tools.common.result_code import ResultCode
from workspace.config.paths import get_api_key_path

# === 工具模組 ===
from workspace.tools.file.data_loader import load_json
from workspace.tools.env.config_loader import R88_TRANSFER_IN_URL, BET_AMOUNT_RULE
from workspace.tools.common.rule_helper import extract_number_from_rule

# === 非同步請求 ===
import httpx


def _generate_transfer_no(account: str) -> str:
    """
    產生符合格式的轉帳編號（timestamp + uuid 混合）
    """
    return f"{int(time.time())}{uuid4().hex[:8]}"


async def recharge_wallet_async(account: str) -> int:
    """
    根據下注規則對指定帳號加值（非同步）

    Args:
        account (str): 帳號名稱（如 qa0047）

    Returns:
        int: ResultCode.SUCCESS 或對應錯誤碼
    """
    try:
        amount = extract_number_from_rule(BET_AMOUNT_RULE)

        code, api_data = load_json(get_api_key_path())
        if code != ResultCode.SUCCESS or not api_data:
            return ResultCode.TASK_RECHARGE_EXCEPTION

        pf_id = api_data.get("pf_id")
        api_key = api_data.get("api_key")

        headers = {
            "Content-Type": "application/json",
            "pf_id": pf_id,
            "timestamp": "0",
            "api_key": api_key,
        }

        payload = {
            "account": account,
            "transfer_no": _generate_transfer_no(account),
            "transfer_type": "0",
            "amount": amount,
        }

        async with httpx.AsyncClient(timeout=5) as client:
            res = await client.post(R88_TRANSFER_IN_URL, headers=headers, json=payload)

        try:
            res_json = res.json()
        except Exception:
            return ResultCode.TASK_RECHARGE_EXCEPTION

        if res_json.get("code") == 0:
            return ResultCode.SUCCESS

        return ResultCode.TASK_RECHARGE_FAILED

    except Exception:
        return ResultCode.TASK_RECHARGE_EXCEPTION
