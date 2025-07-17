import os
from datetime import datetime
from pathlib import Path
from typing import Union


def write_log_line(file_path: Union[str, Path], message: str, timestamp: bool = True):
    """
    將一行訊息寫入指定檔案，可選擇是否加上時間戳。
    
    Args:
        file_path (Union[str, Path]): 寫入的完整檔案路徑
        message (str): 要寫入的文字內容（單行）
        timestamp (bool): 是否加上時間戳（預設為 True）
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if timestamp:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{now}] {message}"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(message.strip() + "\n")
