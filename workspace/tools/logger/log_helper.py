from datetime import datetime
from pathlib import Path
from workspace.tools.printer.printer import print_error, print_success, print_warning



def log_result(code: int, msg: str) -> None:
    """
    根據錯誤碼格式化輸出訊息，附帶標籤與顏色。
    """
    if code == 0:
        print_success(f"[{code}] {msg}")
    elif 40000 <= code <= 49999:
        print_warning(f"[{code}] {msg}")
    else:
        print_error(f"[{code}] {msg}")


def write_log(file_path: Path, message: str) -> None:
    """
    將一行訊息寫入指定 log 檔案，會自動加上 timestamp

    Args:
        file_path (Path): 完整檔案路徑，例如 MIN_BET_LOG_PATH
        message (str): 要寫入的一行訊息
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
