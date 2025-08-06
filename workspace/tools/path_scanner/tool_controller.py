# workspace/tools/path_scanner/tool_controller.py

from .structure_scanner import run_structure_scan, get_all_py_files
from .path_checker import scan_file_for_path_issues
from workspace.config.paths import ROOT_DIR

def run_tool_task(task: str, game_type: str) -> int:
    if task == "scan_structure":
        run_structure_scan()
        return 0

    if task == "scan_path_hardcode":
        py_files = get_all_py_files()
        issues_all = []

        for file in py_files:
            issues_all.extend(scan_file_for_path_issues(file))

        if not issues_all:
            print("✅ 沒有發現硬寫路徑")
        else:
            print(f"⚠️ 共發現 {len(issues_all)} 處可疑路徑用法：\n")
            for path, line, kind, code in issues_all:
                print(f"{kind} {path.relative_to(ROOT_DIR)} (line {line})")
                print(f"   → {code}\n")
        return 0

    print(f"❌ [tool_controller] 不支援的工具任務：{task}")
    return 1
