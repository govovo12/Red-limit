import argparse
import asyncio
import platform

# ✅ 修正 Windows 上的 asyncio 相容性（不印 log）
if platform.system() == "Windows":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

from workspace.controller.main_controller import run_main_flow


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, required=True, help="任務代碼")
    parser.add_argument("--type", type=str, required=True, help="流程類型（如 type_2）")
    args = parser.parse_args()

    result = run_main_flow(task=args.task, game_type=args.type)
    exit(result)
