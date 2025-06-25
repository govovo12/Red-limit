from workspace.tools.printer.printer import print_error,print_info
from workspace.tools.common.result_code import ResultCode

def get_valid_oid_list_from_response(response: dict):
    """
    擷取 game_option_list 中 game_type == 2 的 group 裡的所有遊戲 oid。
    """
    try:
        option_list = response["data"]["game_option_list"]
    except (KeyError, TypeError):
        print_error("❌ 找不到 game_option_list")
        return ResultCode.TASK_GET_GAME_RULE_FAILED

    valid_oids = []
    for group in option_list:
        if str(group.get("game_type")) != "2":  # 注意回傳的是字串
            continue
        for game in group.get("game_option", []):  # ⚠️ 是 game_option，不是 game_list
            oid = game.get("oid")
            if isinstance(oid, int):
                valid_oids.append(oid)

    if not valid_oids:
        print_error("⚠️ 沒有符合條件的 OID（game_type = 2）")
        return ResultCode.TASK_GET_GAME_RULE_FAILED

    print_info(f"✅ 成功擷取 {len(valid_oids)} 筆 OID")
    return valid_oids


