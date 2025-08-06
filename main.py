import sys
import os
import io
from pathlib import Path

# ✅ 初始化 PYTHONPATH + 載入 .env（支援 PyInstaller 模式）
from workspace.init_env import setup
setup()

# ✅ 強制 stdout/stderr 為 utf-8（避免 Windows cp950 地雷）
if sys.stdout and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 🧠 動態定位 base path（打包後是 _MEIPASS，開發中是本機路徑）
if getattr(sys, "frozen", False):
    BASE_PATH = Path(sys._MEIPASS)
else:
    BASE_PATH = Path(__file__).resolve().parent

# ✅ 所有 workspace 的 import 現在才可以安全進行
from workspace.controller import main_controller
from workspace.tools.path_scanner import tool_controller
import argparse
import asyncio
import platform
import functools

# ✅ 支援 flush print
print = functools.partial(print, flush=True)

# ✅ Windows event loop 修正（PyQt）
if platform.system() == "Windows":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="setup_gui", help="任務代碼")
    parser.add_argument("--type", type=str, default="dummy", help="流程類型（如 type_2）")

    args = parser.parse_args()

    # ✅ 工具任務
    if args.task.startswith("scan_"):
        result = tool_controller.run_tool_task(task=args.task, game_type=args.type)

    # ✅ GUI 任務
    elif args.task == "setup_gui":
        from workspace.gui.setup_config_gui_qt import setup_config_gui_controller
        setup_config_gui_controller.main()
        result = 0

    # ✅ 一般任務
    else:
        result = main_controller.run_main_flow(task=args.task, game_type=args.type)

    sys.exit(result)
