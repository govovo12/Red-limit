import re
from decimal import Decimal, InvalidOperation, getcontext

getcontext().prec = 12  # 可依需求調整精度

def check_bet_amount_rule(rule_expr: str, value: float) -> bool:
    """
    根據 rule_expr (如 ">=0.1") 檢查 value 是否符合限紅規則。
    使用 Decimal 進行精確比較，避免浮點誤差。
    """
    rule_expr = rule_expr.strip()

    match = re.match(r"^(>=|<=|==|>|<|!=)\s*(\d+(?:\.\d+)?)$", rule_expr)
    if not match:
        return False

    op, threshold_str = match.groups()

    try:
        threshold = Decimal(threshold_str)
        value_decimal = Decimal(str(value))  # ⭐關鍵：用字串轉 Decimal 避免 float 精度誤差
    except InvalidOperation:
        return False

    if op == "==":
        return value_decimal == threshold
    elif op == "!=":
        return value_decimal != threshold
    elif op == ">":
        return value_decimal > threshold
    elif op == "<":
        return value_decimal < threshold
    elif op == ">=":
        return value_decimal >= threshold
    elif op == "<=":
        return value_decimal <= threshold
    else:
        return False
