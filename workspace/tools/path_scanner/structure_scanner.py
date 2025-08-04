from workspace.config import paths
from pathlib import Path

ROOT_DIR = paths.ROOT_DIR

IGNORED_DIRS = {
    "venv", "__pycache__", ".cache", ".pytest_cache", ".mypy_cache",
    ".idea", ".vscode", ".git", "node_modules"
}

IGNORED_FILES_SUFFIXES = (
    ".pyc", ".pyo"
)

IGNORED_FILES_NAMES = {
    ".gitignore", ".gitattributes", ".gitmodules"
}

def scan_directory_structure(base_dir: Path, indent: int = 0):
    for item in sorted(base_dir.iterdir()):
        if item.is_dir():
            if item.name in IGNORED_DIRS:
                print("    " * indent + f"🚫 {item.name}/")
                continue
            print("    " * indent + f"📂 {item.name}/")
            scan_directory_structure(item, indent + 1)
        elif item.is_file():
            if item.name in IGNORED_FILES_NAMES or item.suffix in IGNORED_FILES_SUFFIXES:
                continue
            print("    " * indent + f"📄 {item.name}")

def run_structure_scan():
    print(f"🔍 Scanning from ROOT_DIR = {ROOT_DIR}")
    scan_directory_structure(ROOT_DIR)

def get_all_py_files(base_dir: Path = ROOT_DIR) -> list[Path]:
    py_files = []
    for item in base_dir.iterdir():
        if item.is_dir():
            if item.name in IGNORED_DIRS:
                continue
            py_files.extend(get_all_py_files(item))
        elif item.is_file():
            if item.name in IGNORED_FILES_NAMES or item.suffix in IGNORED_FILES_SUFFIXES:
                continue
            if item.suffix == ".py":
                py_files.append(item)
    return py_files
