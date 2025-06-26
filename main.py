from workspace.controller.login.r88_login_controller import r88_login_flow
from workspace.controller.ws.ws_connection_controller import ws_connection_flow
from workspace.controller.ws.run_all_oid_controller import run_ws_for_all_oids  
from workspace.tools.printer.printer import print_info, print_error
from workspace.controller.batch.ws_batch_controller_dev import run_ws_batch_dev

import sys
sys.dont_write_bytecode = True

def execute_all_tasks():
    """
    任務 001 + 002：先登入、產生快取，再驗證初始化封包（單筆）
    """
    account = "qa0002"

    print_info("🔐 [1/2] 執行任務 001：登入與快取...")
    login_code = r88_login_flow(account)
    if login_code != 0:
        print_error(f"❌ 任務 001 失敗，錯誤碼：{login_code}")
        return

    print_info("📦 [2/2] 執行任務 002：驗證初始化封包（單筆）...")
    ws_code = ws_connection_flow()
    if ws_code != 0:
        print_error(f"❌ 任務 002 失敗，錯誤碼：{ws_code}")

def execute_all_tasks_multiple_oid():
    """
    任務 001 + 002_ALL：先登入，再逐筆驗證所有 OID 的初始化封包
    """
    account = "qa0002"

    print_info("🔐 [1/2] 執行任務 001：登入與快取...")
    login_code = r88_login_flow(account)
    if login_code != 0:
        print_error(f"❌ 任務 001 失敗，錯誤碼：{login_code}")
        return

    print_info("📦 [2/2] 執行任務 002_ALL：依序驗證所有 OID...")
    run_ws_for_all_oids(account)
    
def execute_login_only():
    """
    任務 001：只執行登入與快取，不跑 WebSocket
    """
    account = "qa0002"
    print_info("🔐 任務 001：執行登入與快取...")
    r88_login_flow(account)

def execute_batch_dev(game_type="type_2"):
    """
    任務 009：執行陽春版 batch controller（測試用）
    """
    run_ws_batch_dev(game_type)

def execute_login_then_batch_dev(game_type="type_2"):
    """
    任務 001+009：先登入再執行陽春版 batch controller
    """
    account = "qa0002"
    print_info("🔐 任務 001：登入與快取...")
    login_code = r88_login_flow(account)
    if login_code != 0:
        print_error(f"❌ 任務 001 失敗，錯誤碼：{login_code}")
        return

    print_info("📦 任務 009：執行陽春 batch 測試...")
    run_ws_batch_dev(game_type)

TASK_MAPPING = {
    "001": execute_login_only,
    "001+002": execute_all_tasks,
    "001+002_ALL": execute_all_tasks_multiple_oid,
}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Red-limit 任務控制入口")
    parser.add_argument("--task", type=str, help="要執行的任務代號")
    parser.add_argument("--type", type=str, default="type_2", help="指定測試類型（type_1/type_2/type_3/ALL）")
    args = parser.parse_args()

    print_info(f"🧩 DEBUG: 收到 args.task = {args.task}")

    if args.task == "009":
        print_info(f"✅ 執行任務 009（type={args.type}）")
        execute_batch_dev(args.type)
    elif args.task == "001+009":
        print_info(f"✅ 執行任務 001+009（type={args.type}）")
        execute_login_then_batch_dev(args.type)
    elif args.task in TASK_MAPPING:
        print_info(f"✅ 執行任務：{args.task}")
        TASK_MAPPING[args.task]()
    else:
        print_error(f"❌ 找不到任務：{args.task}")
