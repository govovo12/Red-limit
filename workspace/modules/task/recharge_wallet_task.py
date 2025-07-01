"""
錢包加值任務模組（新版 API）

根據下注金額規則自動加值最低金額給指定帳號，透過新版平台轉帳 API 發送請求。
"""

import time
from uuid import uuid4

# 🔽 錯誤碼與路徑
from workspace.tools.common.result_code import ResultCode
from workspace.config.paths import get_api_key_path

# 🔽 工具模組
from workspace.tools.file.data_loader import load_json
from workspace.tools.env.config_loader import R88_TRANSFER_IN_URL, BET_AMOUNT_RULE
from workspace.tools.network.request_handler import safe_post
from workspace.tools.common.rule_helper import extract_number_from_rule

def _generate_transfer_no(account: str) -> str:
    """產生符合規則的轉帳編號"""
    return f"{int(time.time())}{uuid4().hex[:8]}"

def recharge_wallet(account: str) -> int:
    print("[RECHARGE MODULE ACTIVE] 🧪")
    """
    根據下注規則對指定帳號加值

    Args:
        account (str): 純帳號（如 qa0047）

    Returns:
        int: ResultCode.SUCCESS 或錯誤碼
    """
    try:
        # ⬇️ 解析金額
        amount = extract_number_from_rule(BET_AMOUNT_RULE)

        # ⬇️ 讀取 pf_id / api_key
        code, api_data = load_json(get_api_key_path())
        if code != ResultCode.SUCCESS or not api_data:
            return ResultCode.TASK_RECHARGE_EXCEPTION

        pf_id = api_data.get("pf_id")
        api_key = api_data.get("api_key")

        # ⬇️ 組 headers
        headers = {
            "Content-Type": "application/json",
            "pf_id": pf_id,
            "timestamp": "0",
            "api_key": api_key,
        }

        # ⬇️ 組 payload
        payload = {
            "account": account,
            "transfer_no": _generate_transfer_no(account),
            "transfer_type": "0",
            "amount": amount,
        }

        # ⬇️ 發送 POST 請求
        res = safe_post(R88_TRANSFER_IN_URL, headers=headers, json=payload, timeout=5)
        if res is None:
            return ResultCode.TASK_RECHARGE_EXCEPTION
        print(f"[DEBUG] 回傳內容：{res.text}")

        res_json = res.json()
        if res_json.get("code") == 0:
            return ResultCode.SUCCESS

        return ResultCode.TASK_RECHARGE_FAILED

    except Exception:
        return ResultCode.TASK_RECHARGE_EXCEPTION
