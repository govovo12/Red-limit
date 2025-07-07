from workspace.tools.env.config_loader import BET_AMOUNT_RULE
from workspace.tools.printer.printer import print_info
from workspace.tools.common.result_code import ResultCode
from workspace.tools.assertion.rule_checker import check_bet_amount_rule


def validate_bet_limit(bet_limit: int) -> int:
    """
    使用 check_bet_amount_rule 判斷 bet_limit 是否符合 .env 設定的限紅條件
    """
    try:
        rule = BET_AMOUNT_RULE
        if check_bet_amount_rule(rule, bet_limit):
            print_info(f"🎯 限紅比對成功：{bet_limit} 符合 {rule}")
            return ResultCode.SUCCESS
        else:
            print_info(f"❌ 限紅比對失敗：{bet_limit} 不符合 {rule}")
            return ResultCode.TASK_BET_MISMATCHED
    except Exception as e:
        print_info(f"[EXCEPTION] 限紅比對錯誤：{e}")
        return ResultCode.TASK_BET_MISMATCHED
