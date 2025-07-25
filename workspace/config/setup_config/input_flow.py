from workspace.tools.common.result_code import ResultCode


def ask_bet_level_mode() -> tuple[str | None, int]:
    print("請選擇限紅模式：")
    print("  1. 最大限紅（max）")
    print("  2. 最小限紅（min）")
    print("")

    mapping = {
        "1": "max",
        "2": "min"
    }

    choice = input("請輸入對應數字 [1 or 2]: ").strip()
    if choice not in mapping:
        return None, ResultCode.TASK_INVALID_BET_LEVEL_MODE
    return mapping[choice], ResultCode.SUCCESS


def ask_bet_rule() -> tuple[str | None, int]:
    print("請選擇限紅條件運算方式：")
    print("  1. 大於（>）")
    print("  2. 小於（<）")
    print("  3. 大於等於（>=）")
    print("  4. 小於等於（<=）")
    print("  5. 等於（==）")
    print("  6. 不等於（!=）")
    print("")

    operator_mapping = {
        "1": ">",
        "2": "<",
        "3": ">=",
        "4": "<=",
        "5": "==",
        "6": "!="
    }

    op_choice = input("請輸入對應數字 [1~6]: ").strip()
    if op_choice not in operator_mapping:
        return None, ResultCode.TASK_INVALID_BET_RULE_OPERATOR

    operator = operator_mapping[op_choice]

    value = input("請輸入限紅數值（例如 10 或 0.05）: ").strip()
    try:
        float(value)
    except ValueError:
        return None, ResultCode.TASK_INVALID_BET_RULE_VALUE

    return f"{operator}{value}", ResultCode.SUCCESS
