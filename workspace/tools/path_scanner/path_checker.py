# workspace/tools/path_scanner/path_checker.py

import re
from pathlib import Path

# 危險模式 regex
ABSOLUTE_PATH_REGEX = re.compile(r'["\']([A-Za-z]:\\|\/)[^"\']+["\']')
RELATIVE_PATH_REGEX = re.compile(r'["\']((\./|\.\./)[^"\']+)["\']')
SUBPROCESS_MAIN_REGEX = re.compile(r'subprocess\.run\(\[.*?["\']python["\']\s*,\s*["\']main\.py["\'].*?\]')
OPEN_PATH_REGEX = re.compile(r'\b(open|read|write|load|save)[(]\s*["\'][^"\']+["\']')

IGNORED_PREFIXES = ('paths.', 'ROOT_DIR /', 'Path(', 'os.path.join(')

def scan_file_for_path_issues(file_path: Path) -> list[tuple[Path, int, str, str]]:
    issues = []
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return [(file_path, 0, "⚠️ 無法解碼", "binary or non-utf8 file")]

    for lineno, line in enumerate(lines, 1):
        if not line.strip() or line.strip().startswith("#"):
            continue
        if any(prefix in line for prefix in IGNORED_PREFIXES):
            continue

        if ABSOLUTE_PATH_REGEX.search(line):
            issues.append((file_path, lineno, "⛔ 絕對路徑", line.strip()))
        elif RELATIVE_PATH_REGEX.search(line):
            issues.append((file_path, lineno, "⛔ 相對路徑", line.strip()))
        elif SUBPROCESS_MAIN_REGEX.search(line):
            issues.append((file_path, lineno, "⛔ subprocess 未包裝 main.py", line.strip()))
        elif OPEN_PATH_REGEX.search(line):
            issues.append((file_path, lineno, "⚠️ open()/read()/write() 路徑未包裝", line.strip()))

    return issues
