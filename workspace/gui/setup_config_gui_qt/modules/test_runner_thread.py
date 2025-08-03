import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

class TestRunnerThread(QThread):
    progress_updated = pyqtSignal(int, str)
    log_updated = pyqtSignal(str)
    finished = pyqtSignal(int)

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
                encoding="utf-8"
            ) as proc:
                if self.log_file:
                    with open(self.log_file, "w", encoding="utf-8") as f:
                        for line in proc.stdout:
                            line = line.strip()
                            f.write(line + "\n")
                            self.log_updated.emit(line)

                            # ✅ 真實進度偵測：格式 [PROGRESS] 60% 任務中...
                            if line.startswith("[PROGRESS]"):
                                try:
                                    percent_str = line.split()[1]
                                    percent = int(percent_str.replace("%", ""))
                                    msg = " ".join(line.split()[2:])
                                    self.progress_updated.emit(percent, msg)
                                except:
                                    pass  # 解析錯誤不影響 log

                proc.wait()
                self.progress_updated.emit(100, "完成")
                self.finished.emit(proc.returncode)

        except Exception as e:
            self.log_updated.emit(f"[錯誤] 無法執行：{e}")
            self.progress_updated.emit(0, "錯誤")
            self.finished.emit(1)
