# workspace/controller/batch/ws_batch_controller_dev.py

"""
陽春版子控：用於測試各 game_type 對應的任務模組（支援 type_1, type_2, type_3, ALL）
可從 CLI 呼叫，例如：
    python ws_batch_controller_dev.py type_2
    python ws_batch_controller_dev.py ALL
"""

import sys
from concurrent.futures import ThreadPoolExecutor
from workspace.modules.batch.prepare_oid_list_by_type import get_oid_list_by_type
from workspace.modules.batch.generate_account_oid_pairs import generate_account_oid_pairs
from workspace.modules.batch.login_task import run_login_task
from workspace.modules.batch.get_access_token_task import get_access_token_task
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info, print_error


def run_type_batch(game_type: str):
    print_info(f"[DEV] 🎮 測試流程：{game_type} → 取得 OID 清單")
    code, raw_result = get_oid_list_by_type(game_type)

    if code != ResultCode.SUCCESS:
        print_error(f"[DEV] ❌ 錯誤碼：{code}，讀取 OID 清單失敗")
        return

    if game_type == "ALL":
        oid_list = []
        for type_key, entries in raw_result.items():
            oid_list.extend(entries)
    else:
        oid_list = raw_result

    print_info(f"[DEV] ✅ 共取得 {len(oid_list)} 個 OID，準備產生帳號配對...")
    account_oid_pairs = generate_account_oid_pairs(oid_list, prefix="qa")

    print_info(f"[DEV] ✅ 已產生帳號配對清單，共 {len(account_oid_pairs)} 組")

    print_info("[DEV] 🚀 開始執行多線登入任務（取得 lobby_token）...")
    with ThreadPoolExecutor(max_workers=len(account_oid_pairs)) as pool:
        login_results = list(pool.map(run_login_task, account_oid_pairs))

    print_info("[DEV] 🧾 登入結果統整：")
    success_count = 0
    fail_count = 0

    for i, (task, code) in enumerate(zip(account_oid_pairs, login_results)):
        if code == ResultCode.SUCCESS:
            success_count += 1
        else:
            fail_count += 1

    print_info(f"[DEV] 📊 成功登入帳號數量：{success_count}/{len(account_oid_pairs)}")
    print_info(f"[DEV] 📊 登入失敗帳號數量：{fail_count}/{len(account_oid_pairs)}")

  

    print_info("[DEV] 🚀 開始執行多線取得 access_token 任務...")
    with ThreadPoolExecutor(max_workers=len(account_oid_pairs)) as pool:
        access_token_results = list(pool.map(get_access_token_task, account_oid_pairs))

    print_info("[DEV] 🧾 access_token 統整結果：")
    access_success = 0
    access_fail = 0

    # ✅ 先清掉所有 lobby_token
    for t, _ in access_token_results:
        t.pop("lobby_token", None)

# ✅ 然後開始列印與統計（這時已經沒有 lobby_token 了）
    for i, (task, code) in enumerate(access_token_results):
        if i == 0:
            print_info("[DEV] ✅ 第一筆取得 access_token 結果（已清除 lobby_token）：")
            print_info(f"  account: {task['account']}")
            print_info(f"  oid: {task['oid']}")
            print_info(f"  game_name: {task['game_name']}")
            print_info(f"  type: {task['type']}")
            print_info(f"  access_token: {task.get('access_token', '---')}")
            print_info(f"  status: {'SUCCESS' if code == ResultCode.SUCCESS else f'FAIL ({code})'}")

        if code == ResultCode.SUCCESS:
            access_success += 1
        else:
            access_fail += 1

    print_info(f"[DEV] 📊 成功取得 access_token 數量：{access_success}/{len(account_oid_pairs)}")
    print_info(f"[DEV] 📊 失敗取得 access_token 數量：{access_fail}/{len(account_oid_pairs)}")


def run_ws_batch_dev(game_type: str):
    print_info(f"[DEV] 🧪 啟動測試類型：{game_type}")

    dispatch_map = {
        "type_1": lambda: run_type_batch("type_1"),
        "type_2": lambda: run_type_batch("type_2"),
        "type_3": lambda: run_type_batch("type_3"),
        "ALL": lambda: run_type_batch("ALL"),
    }

    if game_type not in dispatch_map:
        print_error(f"[DEV] ⚠️ 不支援的類型：{game_type}")
        return

    dispatch_map[game_type]()


if __name__ == "__main__":
    game_type = sys.argv[1] if len(sys.argv) > 1 else "type_2"
    run_ws_batch_dev(game_type)
