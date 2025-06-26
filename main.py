# main.py

from workspace.controller.main_controller import run_main_flow
from workspace.tools.printer.printer import print_info, print_error

import sys
sys.dont_write_bytecode = True

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Red-limit 任務控制入口")
    parser.add_argument("--task", type=str, required=True, help="要執行的任務代號，例如 001、009、001+009")
    parser.add_argument("--type", type=str, default="type_2", help="指定測試類型（type_1/type_2/type_3/ALL）")
    args = parser.parse_args()

    print_info(f"🧩 DEBUG: 收到 args.task = {args.task}")
    result = run_main_flow(task=args.task, game_type=args.type)

    if result != 0:
        print_error(f"❌ 任務 {args.task} 執行失敗，錯誤碼：{result}")