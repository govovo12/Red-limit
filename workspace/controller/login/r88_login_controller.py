from workspace.modules.login.get_lobby_info import get_lobby_token
from workspace.modules.login.login_to_r88_account import login_to_r88_account
from workspace.modules.login.get_game_option_response import fetch_game_option_response
from workspace.modules.login.generate_r88_api_key import generate_r88_api_key
from workspace.modules.login.prepare_game_classification_input import prepare_game_classification_input
from workspace.modules.login.save_oid_map_to_cache import save_oid_map_to_cache
from workspace.modules.login.count_oid_entries import count_oid_entries  # ✅ 第八步用

from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.common.decorator import task


@task("001")
def r88_login_flow(account: str) -> int:
    """
    子控制器流程：產生 API 金鑰並登入 R88，完成 OID 快取與統計。
    共 8 步驟，使用者僅需輸入帳號。
    """

    # Step 1: 產生 API Key
    print_info("🧩 Step 1：產生 API 金鑰")
    code = generate_r88_api_key()
    if code != ResultCode.SUCCESS:
        log_step_result(code, step="generate_api_key", account=account)
        return code

    # Step 2: 取得大廳 token
    print_info("🧩 Step 2：取得大廳 token")
    code = get_lobby_token(account)
    if code != ResultCode.SUCCESS:
        log_step_result(code, step="get_lobby_info", account=account)
        return code

    # Step 3: 登入 R88 帳號
    print_info("🧩 Step 3：登入帳號")
    code = login_to_r88_account(account)
    if code != ResultCode.SUCCESS:
        log_step_result(code, step="login_to_r88_account", account=account)
        return code

    # Step 4: 拉取遊戲列表
    print_info("🧩 Step 4：拉取遊戲列表")
    response = fetch_game_option_response(account)
    if isinstance(response, int):
        log_step_result(response, step="fetch_game_option_response", account=account)
        return response

    # Step 5: 準備分類結果（已內建分群）
    print_info("🧩 Step 5：準備分類輸入資料")
    code, oid_map = prepare_game_classification_input(response)
    if code != ResultCode.SUCCESS:
        log_step_result(code, step="prepare_classification_input", account=account)
        return code


    # Step 7: 儲存快取檔
    print_info("🧩 Step 7：儲存快取檔 (.cache/oid_by_type.json)")
    code = save_oid_map_to_cache(oid_map)
    if code != ResultCode.SUCCESS:
        log_step_result(code, step="save_oid_cache", account=account)
        return code

    # Step 8: 統計總 OID 數量
    print_info("🧩 Step 8：統計 OID 數量")
    code, stats = count_oid_entries(oid_map)
    if code != ResultCode.SUCCESS:
        log_step_result(code, step="count_oid_entries", account=account)
        return code

    print("==================================================================")  # ✅ 純分隔線，不帶 INFO

    for type_key, count in stats.items():
        if type_key != "total":
            print_info(f"{type_key}：{count} 筆")
    print_info(f"📊 共成功取得 {stats['total']} 筆 OID")

    return ResultCode.SUCCESS

