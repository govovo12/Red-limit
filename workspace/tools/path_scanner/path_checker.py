# workspace/tools/path_scanner/path_checker.py

import re
from pathlib import Path

HARD_PATH_REGEX = re.compile(
    r'(?<!paths\.)(?<!Path\()(?<!os\.path\.join\()'   # 不以 paths/Path 開頭
    r'(["\'])(\.{1,2}/|[A-Za-z]:\\|/)[^"\']+\1'        # 類似硬寫路徑
)

def scan_paths_for_hardcode(py_paths: list[Path]):
    print("🔍 Scanning for hardcoded paths in .py files...\n")

    issues_found = 0

    for file_path in py_paths:
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            print(f"⚠️ 無法解碼：{file_path}")
            continue

        for lineno, line in enumerate(lines, start=1):
            match = HARD_PATH_REGEX.search(line)
            if match:
                issues_found += 1
                print(f"⛔ {file_path} (line {lineno})")
                print(f"   → {line.strip()}\n")

    if issues_found == 0:
        print("✅ 沒有發現疑似硬寫路徑！")
    else:
        print(f"⚠️ 共發現 {issues_found} 處疑似硬寫路徑")
