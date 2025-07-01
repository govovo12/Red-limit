"""
錢包加值任務模組

根據下注金額規則自動加值最低金額給指定帳號。
"""

from workspace.tools.env.config_loader import (
    PF_ID,
    R88_TRANSFER_IN_URL,
    BET_AMOUNT_RULE,
)
from workspace.tools.network.request_handler import safe_post
from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.rule_helper import extract_number_from_rule
from workspace.tools.printer.printer import print_error

def recharge_wallet(account: str) -> int:
    """
    根據下注規則對指定帳號加值

    Args:
        account (str): 純帳號（如 qa0047）

    Returns:
        int: ResultCode.SUCCESS 或錯誤碼
    """
    try:
        pf_account = f"{PF_ID}{account}"
        amount = extract_number_from_rule(BET_AMOUNT_RULE)

        payload = {
            "pf_account": pf_account,
            "money": amount,
        }

        headers = {"Content-Type": "application/json"}

        res = safe_post(R88_TRANSFER_IN_URL, headers=headers, json=payload, timeout=5)
        if res is None:
            return ResultCode.TASK_RECHARGE_EXCEPTION

        res_json = res.json()
        if res_json.get("success") is True or res_json.get("code") == 0:
            return ResultCode.SUCCESS
        print_error(f"[recharge_wallet] ❌ 加值失敗 pf_account={pf_account} res={res_json}")
        return ResultCode.TASK_RECHARGE_FAILED

    except Exception:
        return ResultCode.TASK_RECHARGE_EXCEPTION
