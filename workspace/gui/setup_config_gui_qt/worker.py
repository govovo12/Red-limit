from PyQt5.QtCore import QThread, pyqtSignal
import subprocess


class TestRunnerThread(QThread):
    """
    在背景執行 CLI 任務，執行結束後發出 finished(int) 訊號。
    可用於 GUI 控制流程中非同步執行 main.py 並回傳 exit code。
    """
    finished = pyqtSignal(int)  # 回傳 exit code

    def __init__(self, cmd, cwd, env, log_path):
        super().__init__()
        self.cmd = cmd
        self.cwd = cwd
        self.env = env
        self.log_path = log_path

    def run(self):
        with open(self.log_path, "w", encoding="utf-8") as f:
            result = subprocess.run(
                self.cmd,
                cwd=self.cwd,
                env=self.env,
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8"
            )
        self.finished.emit(result.returncode)
