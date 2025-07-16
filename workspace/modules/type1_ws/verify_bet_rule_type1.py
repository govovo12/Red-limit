from workspace.tools.env.config_loader import BET_AMOUNT_RULE
from workspace.tools.common.result_code import ResultCode
from workspace.tools.assertion.rule_checker import check_bet_amount_rule


async def validate_bet_limit_type1(bet_limit: int) -> int:
    """
    判斷 bet_limit 是否符合 .env 設定的限紅條件（type 1 用）。
    比對成功則回傳 SUCCESS，否則回傳 TASK_BET_MISMATCHED。
    """
    try:
        rule = BET_AMOUNT_RULE
        if check_bet_amount_rule(rule, bet_limit):
            return ResultCode.SUCCESS
        else:
            return ResultCode.TASK_BET_MISMATCHED
    except Exception:
        return ResultCode.TASK_BET_MISMATCHED
