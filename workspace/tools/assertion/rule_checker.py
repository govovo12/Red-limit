import re

def check_bet_amount_rule(rule_expr: str, value: float) -> bool:
    rule_expr = rule_expr.strip()
    print(f"[DEBUG] 清理後的 rule_expr: {repr(rule_expr)}")

    try:
        match = re.match(r"^(>=|<=|==|>|<|!=)\s*(\d+(?:\.\d+)?)$", rule_expr)
        if not match:
            print(f"[DEBUG] ❌ 無法解析規則字串：{repr(rule_expr)}")
            return False

        op, threshold = match.groups()
        threshold = float(threshold)
        value = float(value)

        if op == "==":
            result = value == threshold
            print(f"[DEBUG] 實際比對：float({value}) == float({threshold}) → {result}")
            return result
        elif op == "!=":
            return value != threshold
        elif op == ">":
            return value > threshold
        elif op == "<":
            return value < threshold
        elif op == ">=":
            return value >= threshold
        elif op == "<=":
            return value <= threshold
        else:
            return False

    except Exception as e:
        print(f"[DEBUG] ❌ 比對過程中發生例外：{e}")
        return False
