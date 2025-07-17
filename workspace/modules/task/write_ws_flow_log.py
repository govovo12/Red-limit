from datetime import datetime
from pathlib import Path

from workspace.tools.logger.file_logger import write_log_line


_current_log_path: Path | None = None


def init_log_file(game_type: str):
    """
    初始化 log 檔案：
    - 若 log 資料夾不存在，建立
    - 若 type 資料夾不存在，建立
    - 若 log 檔案存在，砍掉重建；不存在就建立
    """
    global _current_log_path

    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = Path("log") / game_type
    log_dir.mkdir(parents=True, exist_ok=True)  # 建立資料夾（含父層）

    _current_log_path = log_dir / f"{date_str}_{game_type}.txt"

    # 無論檔案是否存在，直接覆蓋寫入
    _current_log_path.write_text(f"[INIT] 建立 {game_type} log 檔案\n", encoding="utf-8")



def write_log(text: str, *, timestamp: bool = False):
    """
    寫入一行文字到目前 log 檔案（需先執行 init_log_file），預設不加時間戳
    """
    if _current_log_path is None:
        raise RuntimeError("請先呼叫 init_log_file() 初始化 log 檔案")

    write_log_line(_current_log_path, text, timestamp=timestamp)
