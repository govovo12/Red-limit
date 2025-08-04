import subprocess
from PyQt5.QtCore import QThread, pyqtSignal


class TestRunnerThread(QThread):
    progress_updated = pyqtSignal(int, str)
    log_updated = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, command, log_file=None, cwd=None, env=None):
        super().__init__()
        self.command = command  # ✅ 建議外部傳入時包含 "python -u"
        self.log_file = log_file
        self.cwd = cwd
        self.env = env

    def run(self):
        try:
            with subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                cwd=self.cwd,
                env=self.env,
                bufsize=1
            ) as proc:
                if self.log_file:
                    with open(self.log_file, "w", encoding="utf-8") as f:
                        while True:
                            line = proc.stdout.readline()
                            if not line:
                                break
                            line = line.strip()
                            f.write(line + "\n")
                            self.log_updated.emit(line)

                            # ✅ 額外解析 [PROGRESS] 顯示
                            if line.startswith("[PROGRESS]"):
                                try:
                                    percent_str = line.split()[1]
                                    percent = int(percent_str.replace("%", ""))
                                    msg = " ".join(line.split()[2:])
                                    self.progress_updated.emit(percent, msg)
                                except:
                                    pass

                proc.wait()
                self.progress_updated.emit(100, "完成")
                self.finished.emit(proc.returncode)

        except Exception as e:
            self.log_updated.emit(f"[錯誤] 無法執行：{e}")
            self.progress_updated.emit(0, "錯誤")
            self.finished.emit(1)
