from pathlib import Path
from datetime import datetime

LOG_DIR = Path(".log")
LOG_DIR.mkdir(exist_ok=True)

def get_log_filename(base_name: str) -> str:
    """
    自動依據日期產生 log 檔名。
    例如 base_name 為 'game_min_bet_all'，則產生 'game_min_bet_all_2025-06-16.log'
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    return f"{base_name}_{today_str}.log"

def write_log(base_name: str, message: str, log_dir: Path):
    """
    將 log 訊息寫入對應 log 檔案，並加上時間戳。
    
    :param base_name: log 類型名稱（不含副檔名），例如 'game_min_bet_all'
    :param message: 要寫入的訊息內容
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = get_log_filename(base_name)
    full_path = log_dir / filename
    with open(full_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
