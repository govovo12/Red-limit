from workspace.modules.login.get_lobby_info import get_lobby_token
from workspace.modules.login.login_to_r88_account import login_to_r88_account
from workspace.modules.login.get_game_option_response import fetch_game_option_response
from workspace.modules.login.get_valid_oid_list import get_valid_oid_list_from_response
from workspace.modules.login.generate_r88_api_key import generate_r88_api_key
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.decorator import task


@task("001")
def r88_login_flow(account: str) -> int:
    """
    子控制器流程：
      [1/5] 產生 API Key
      [2/5] 取得大廳資訊
      [3/5] 登入 R88 帳號
      [4/5] 拉取遊戲列表
      [5/5] 擷取符合條件的 OID 並快取
    Args:
        account (str): 登入帳號（例如 qa0002）
    Returns:
        int: 最終錯誤碼，0 表示成功
    """
    print_info("🚀 [1/5] 產生 API Key...")
    generate_r88_api_key()

    print_info("📥 [2/5] 取得大廳資訊...")
    code = get_lobby_token(account)
    if code != 0:
        print_error(f"❌ get_lobby_info 失敗，錯誤碼：{code}")
        return code

    print_info(f"🔑 [3/5] 登入帳號 {account}...")
    code = login_to_r88_account(account)
    if code != 0:
        print_error(f"❌ login_to_r88_account 失敗，錯誤碼：{code}")
        return code

    print_info("📊 [4/5] 拉取遊戲列表...")
    response = fetch_game_option_response(account)
    if isinstance(response, int):
        print_error(f"❌ fetch_game_option_response 失敗，錯誤碼：{response}")
        return response
    print_info("📄 ✅ 遊戲列表 response 已取得")

    print_info("🔎 [5/5] 擷取並分類 OID 清單...")
    oid_map = get_valid_oid_list_from_response(response)
    if isinstance(oid_map, int):
        print_error(f"❌ 擷取 OID 清單失敗，錯誤碼：{oid_map}")
        return oid_map

    # 統計總數量
    oid_count = sum(len(group) for group in oid_map.values())
    print_info(f"✅ 擷取成功，總共 {oid_count} 筆 OID")
    for type_key, group in oid_map.items():
        print_info(f"- {type_key}：{len(group)} 筆")

    # 💾 寫入快取檔（.cache/oid_by_type.json）
    from workspace.tools.file.data_loader import save_json
    from workspace.config.paths import get_oid_by_type_path

    error_code, ok = save_json(oid_map, get_oid_by_type_path())
    if not ok:
        print_error("❌ 寫入 OID 快取失敗")
        return error_code

    print_info(f"📁 OID 快取已寫入：{get_oid_by_type_path()}")

    return ResultCode.SUCCESS