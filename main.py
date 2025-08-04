from workspace.controller import main_controller
from workspace.tools.path_scanner import tool_controller  # 👈 加這行

import argparse
import asyncio
import platform
import functools
print = functools.partial(print, flush=True)

if platform.system() == "Windows":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, required=True, help="任務代碼")
    parser.add_argument("--type", type=str, required=True, help="流程類型（如 type_2）")
    args = parser.parse_args()

    # ✅ 工具任務交給 tool_controller 控
    if args.task.startswith("scan_"):
        result = tool_controller.run_tool_task(task=args.task, game_type=args.type)
    else:
        # ✅ 主流程交給 main_controller 控（你的 WS 任務、測試流程）
        result = main_controller.run_main_flow(task=args.task, game_type=args.type)

    exit(result)
