import json
from pathlib import Path
from PyQt5.QtCore import QTimer

PROGRESS_FILE = Path(__file__).resolve().parents[3] / ".progress.json"

class ProgressWatcher:
    def __init__(self, progress_dialog, update_interval=1000):
        """
        初始化進度條監控器，負責讀取進度檔案並更新進度條
        :param progress_dialog: 要更新的 QProgressDialog 實例
        :param update_interval: 進度更新的間隔時間，預設 1000 毫秒
        """
        self.progress_dialog = progress_dialog
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(update_interval)
        self.progress_dialog.setLabelText("測試執行中...")

    def update_progress(self):
        try:
            # 讀取 .progress.json 檔案
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                progress_data = json.load(f)
            percent = progress_data.get("percent", 0)
            step = progress_data.get("step", "")

            # 更新進度條顯示
            self.progress_dialog.setValue(percent)
            self.progress_dialog.setLabelText(f"{step} ({percent}%)")

            # 停止計時器，當進度條已經達到 100%
            if percent == 100:
                self.timer.stop()
        except Exception as e:
            # 如果檔案讀取錯誤，則不更新進度條
            pass
            
from PyQt5.QtWidgets import QProgressDialog

def show_progress_dialog():
    """
    顯示一個即時更新的 QProgressDialog，綁定 ProgressWatcher 自動更新 .progress.json
    """
    dialog = QProgressDialog("執行中...", "取消", 0, 100)
    dialog.setWindowTitle("測試進度")
    dialog.setWindowModality(True)
    dialog.setMinimumWidth(400)
    dialog.setValue(0)

    # 啟用監控器
    ProgressWatcher(dialog)
    return dialog
