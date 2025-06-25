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

    print_info("🔎 [5/5] 擷取符合條件的 OID...")
    oids = get_valid_oid_list_from_response(response)
    if isinstance(oids, int):
        print_error(f"❌ 擷取 OID 清單失敗，錯誤碼：{oids}")
        return oids

    print_info(f"✅ 擷取成功，共 {len(oids)} 筆 OID")
    print_info(f"📌 前 5 筆 OID：{oids[:5]}")

    # 💾 將 OID 清單寫入快取檔
    from pathlib import Path
    import json

    cache_path = Path(".cache/oid_list.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(oids, f, indent=2, ensure_ascii=False)

    print_info(f"📁 OID 清單已寫入：{cache_path}")
    return ResultCode.SUCCESS
