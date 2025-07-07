from workspace.modules.login.get_lobby_info import get_lobby_token
from workspace.modules.login.login_to_r88_account import login_to_r88_account
from workspace.modules.login.get_game_option_response import fetch_game_option_response
from workspace.modules.login.generate_r88_api_key import generate_r88_api_key
from workspace.modules.login.prepare_game_classification_input import prepare_game_classification_input
from workspace.modules.login.classify_game_by_type import classify_game_by_type  # ✅ 新增
from workspace.modules.login.save_oid_map_to_cache import save_oid_map_to_cache
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.decorator import task


@task("001")
def r88_login_flow(account: str) -> int:
    """
    子控制器流程（到第六步）：
      [1/6] 產生 API Key
      [2/6] 取得大廳資訊
      [3/6] 登入 R88 帳號
      [4/6] 拉取遊戲列表
      [5/6] 整理分類輸入資料（預備分類）
      [6/6] 執行分類並印出對應類型結果

    Args:
        account (str): 登入帳號（例如 qa0002）

    Returns:
        int: 最終錯誤碼，0 表示成功
    """
    print_info("🚀 [1/6] 產生 API Key...")
    generate_r88_api_key()

    print_info("📥 [2/6] 取得大廳資訊...")
    code = get_lobby_token(account)
    if code != 0:
        print_error(f"❌ get_lobby_info 失敗，錯誤碼：{code}")
        return code

    print_info(f"🔑 [3/6] 登入帳號 {account}...")
    code = login_to_r88_account(account)
    if code != 0:
        print_error(f"❌ login_to_r88_account 失敗，錯誤碼：{code}")
        return code

    print_info("📊 [4/6] 拉取遊戲列表...")
    response = fetch_game_option_response(account)
    if isinstance(response, int):
        print_error(f"❌ fetch_game_option_response 失敗，錯誤碼：{response}")
        return response
    print_info("📄 ✅ 遊戲列表 response 已取得")

    print_info("🔍 [5/6] 整理分類輸入資料（預備分類）...")
    game_type_map, game_data_list = prepare_game_classification_input(response)

    print_info("📦 [6/6] 分類遊戲，依照 type_1 ~ type_4 整理完成...")
    oid_map = classify_game_by_type(game_type_map, game_data_list)
    classify_game_by_type(game_type_map, game_data_list)  # ✅ 印出分類結果

    print_info("💾 [7/7] 儲存快取檔案 (.cache/oid_by_type.json)...")
    code = save_oid_map_to_cache(oid_map)
    if code != ResultCode.SUCCESS:
        print_error(f"❌ 儲存 OID 快取失敗，錯誤碼：{code}")
        return code

    return ResultCode.SUCCESS
  
