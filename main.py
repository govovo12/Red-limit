from workspace.controller.login.r88_login_controller import r88_login_flow
from workspace.controller.ws.ws_connection_controller import ws_connection_flow
from workspace.controller.ws.run_all_oid_controller import run_ws_for_all_oids  
from workspace.tools.printer.printer import print_info, print_error
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


TASK_MAPPING = {
    "001+002": execute_all_tasks,
    "001+002_ALL": execute_all_tasks_multiple_oid,  # 👈 新任務入口
}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Red-limit 任務控制入口")
    parser.add_argument("--task", type=str, help="要執行的任務代號")
    args = parser.parse_args()

    print_info(f"🧩 DEBUG: 收到 args.task = {args.task}")

    if args.task in TASK_MAPPING:
        print_info(f"✅ 執行任務：{args.task}")
        TASK_MAPPING[args.task]()
    else:
        print_error(f"❌ 找不到任務：{args.task}")
