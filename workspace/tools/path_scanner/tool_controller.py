# workspace/tools/path_scanner/tool_controller.py

from .structure_scanner import run_structure_scan, get_all_py_files
from .path_checker import scan_paths_for_hardcode

def run_tool_task(task: str, game_type: str) -> int:
    if task == "scan_structure":
        run_structure_scan()
        return 0

    if task == "scan_path_hardcode":
        py_paths = get_all_py_files()
        scan_paths_for_hardcode(py_paths)
        return 0

    print(f"❌ [tool_controller] 不支援的工具任務：{task}")
    return 1
