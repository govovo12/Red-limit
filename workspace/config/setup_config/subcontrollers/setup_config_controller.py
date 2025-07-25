from workspace.config.setup_config.input_validator import validate_pf_id, validate_private_key
from workspace.config.setup_config.input_flow import ask_bet_level_mode, ask_bet_rule
from workspace.config.setup_config.config_writer import save_env_config
from workspace.tools.retey.retry_helper import retry_with_log
from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.log_helper import log_simple_result


def ask_pfid_input():
    pf_id_input = input("請輸入 PF_ID: ").strip()
    pf_id, code = validate_pf_id(pfid_input := pf_id_input)
    if code != ResultCode.SUCCESS:
        return code
    return {"PF_ID": pf_id}


def ask_private_key_input():
    private_key_input = input("請輸入 PRIVATE_KEY: ").strip()
    private_key, code = validate_private_key(private_key_input)
    if code != ResultCode.SUCCESS:
        return code
    return {"PRIVATE_KEY": private_key}


def ask_bet_level_mode_task():
    mode, code = ask_bet_level_mode()
    if code != ResultCode.SUCCESS:
        return code
    return {"BET_LEVEL_MODE": mode}


def ask_bet_rule_task():
    rule, code = ask_bet_rule()
    if code != ResultCode.SUCCESS:
        return code
    return {"BET_AMOUNT_RULE": rule}


def run_setup_config():
    # Step 1: PF_ID
    pfid_result = retry_with_log(ask_pfid_input, step="輸入 PF_ID")
    pf_id = pfid_result["PF_ID"]

    # Step 2: PRIVATE_KEY
    private_key_result = retry_with_log(ask_private_key_input, step="輸入 PRIVATE_KEY")
    private_key = private_key_result["PRIVATE_KEY"]

    # Step 3: BET_LEVEL_MODE
    bet_mode_result = retry_with_log(ask_bet_level_mode_task, step="選擇 BET_LEVEL_MODE")
    bet_mode = bet_mode_result["BET_LEVEL_MODE"]

    # Step 4: BET_AMOUNT_RULE
    bet_rule_result = retry_with_log(ask_bet_rule_task, step="設定 BET_AMOUNT_RULE")
    bet_rule = bet_rule_result["BET_AMOUNT_RULE"]

    # Step 5: 寫入 .env.user
    data = {
        "PF_ID": pf_id,
        "PRIVATE_KEY": private_key,
        "BET_LEVEL_MODE": bet_mode,
        "BET_AMOUNT_RULE": bet_rule,
    }
    code = save_env_config(data)
    log_simple_result(code)
    return code


if __name__ == "__main__":
    run_setup_config()
