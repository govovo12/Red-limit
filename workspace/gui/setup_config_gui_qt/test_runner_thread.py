import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

class TestRunnerThread(QThread):
    progress_updated = pyqtSignal(int, str)
    log_updated = pyqtSignal(str)
    finished = pyqtSignal(int)  # ✅ 明確 signal 傳整數 code

    def __init__(self, command, cwd=None, env=None, log_file=None):
        super().__init__()
        self.command = command
        self.cwd = cwd
        self.env = env
        self.log_file = log_file

    def run(self):
        try:
            with subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.cwd,
                env=self.env,
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8"  # ✅ 強制解 UTF-8，避免 cp950 出錯
            ) as proc:
                if self.log_file:
                    with open(self.log_file, "w", encoding="utf-8") as f:
                        for i, line in enumerate(proc.stdout, 1):
                            line = line.strip()
                            f.write(line + "\n")
                            self.log_updated.emit(line)
                            self.progress_updated.emit(min(i * 2, 98), line)
                proc.wait()
                self.progress_updated.emit(100, "完成")
                self.finished.emit(proc.returncode)  # ✅ 通知 GUI
        except Exception as e:
            self.log_updated.emit(f"[錯誤] 無法執行：{e}")
            self.progress_updated.emit(0, "錯誤")
            self.finished.emit(1)  # ✅ 異常也要通知 GUI
