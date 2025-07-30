import json
from pathlib import Path

PROGRESS_FILE = Path(__file__).resolve().parents[3] / ".progress.json"

def report_progress(percent: int, step: str = ""):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump({"percent": percent, "step": step}, f, ensure_ascii=False)
    except Exception:
        pass  # 寫入失敗不阻斷主控流程
