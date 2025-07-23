from workspace.tools.env.config_loader import BET_AMOUNT_RULE
from workspace.tools.common.result_code import ResultCode
from workspace.tools.assertion.rule_checker import check_bet_amount_rule


async def validate_bet_limit(bet_limit: int) -> tuple[int, str, int]:
    """
    判斷 bet_limit 是否符合 .env 設定的限紅條件（type 3）

    Returns:
        tuple: (錯誤碼, 預期期限紅規則字串, 實際限紅數值)
    """
    try:
        rule = BET_AMOUNT_RULE
        if check_bet_amount_rule(rule, bet_limit):
            return ResultCode.SUCCESS, rule, bet_limit
        else:
            return ResultCode.TASK_BET_MISMATCHED, rule, bet_limit
    except Exception:
        return ResultCode.TASK_BET_MISMATCHED, BET_AMOUNT_RULE, bet_limit
