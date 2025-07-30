import os
import sys
import json
from time import sleep
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit,
    QVBoxLayout, QHBoxLayout, QMessageBox, QProgressBar, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from workspace.gui.setup_config_gui_qt.validator import load_user_config

def create_page2(stack_widget):
    outer = QWidget()
    layout = QVBoxLayout()

    # 顯示目前設定資訊
    config = load_user_config()
    pfid = config.get("PF_ID", "未設定")
    key = config.get("PRIVATE_KEY", "未設定")
    rule = config.get("BET_AMOUNT_RULE", "未設定")
    level = config.get("BET_LEVEL_MODE", "未設定")

    rule_display = f"下注金額規則：{rule}" if rule else "下注金額規則：未設定"
    level_display = {
        "min": "最小限紅模式",
        "max": "最大限紅模式"
    }.get(level, "未設定")

    lines = [
        f"帳號（PF_ID）：{pfid}",
        f"金鑰（PRIVATE_KEY）：{key}",
        rule_display,
        f"限紅模式：{level_display}"
    ]

    config_label = QLabel("\n".join(lines))
    config_label.setStyleSheet("font-size: 14px;")
    layout.addWidget(config_label)

    # 測試類型選單
    type_label = QLabel("請選擇要執行的測試流程：")
    layout.addWidget(type_label)

    test_type_combo = QComboBox()
    test_type_combo.addItems(["type_1", "type_2", "type_3", "ALL"])
    layout.addWidget(test_type_combo)

    # 內嵌進度條
    progress_bar = QProgressBar()
    progress_bar.setValue(0)
    progress_bar.setFormat("尚未開始")
    layout.addWidget(progress_bar)

    # 結果輸出區
    result_output = QTextEdit()
    result_output.setReadOnly(True)
    layout.addWidget(result_output)

    # 按鈕區
    btn_layout = QHBoxLayout()

    run_button = QPushButton("執行測試")
    btn_layout.addWidget(run_button)

    back_button = QPushButton("返回上一頁")
    btn_layout.addWidget(back_button)

    layout.addLayout(btn_layout)
    outer.setLayout(layout)

    def on_test_finished(code, selected_type):
        # 恢復 UI 元件狀態
        run_button.setEnabled(True)
        back_button.setEnabled(True)
        test_type_combo.setEnabled(True)
        run_button.setText("執行測試")
        QApplication.restoreOverrideCursor()

        if code == 0:
            QMessageBox.information(None, "完成", f"✅ 測試 {selected_type} 完成！")
        else:
            QMessageBox.warning(None, "錯誤", f"❌ 測試 {selected_type} 執行失敗，請查看輸出內容")

    def handle_test_execution():
        selected_type = test_type_combo.currentText()
        result_output.clear()               # ✅ 清空 log 顯示區
        progress_bar.setValue(0)           # ✅ 重設進度條
        progress_bar.setFormat("尚未開始")  # ✅ 清除狀態文字

        if not selected_type:
            QMessageBox.warning(None, "錯誤", "請選擇要執行的測試類型")
            return

        # 鎖定 UI 元件
        run_button.setEnabled(False)
        back_button.setEnabled(False)
        test_type_combo.setEnabled(False)
        run_button.setText("執行中...")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        task_arg = "001+009"
        main_path = Path(__file__).resolve().parents[3] / "main.py"
        log_path = main_path.parent / "last_test.log"

        env = os.environ.copy()
        env["PYTHONPATH"] = str(main_path.parent)
        env["PYTHONIOENCODING"] = "utf-8"

        cmd = [sys.executable, str(main_path), "--task", task_arg, "--type", selected_type]

        outer.thread = TestRunnerThread(cmd, str(main_path.parent), env, log_path)
        outer.thread.progress_updated.connect(lambda p, s: (progress_bar.setValue(p), progress_bar.setFormat(f"{s} (%p%)")))
        outer.thread.log_updated.connect(lambda line: result_output.append(line))
        outer.thread.finished.connect(lambda code: on_test_finished(code, selected_type))
        outer.thread.start()

    def handle_back():
        stack_widget.setCurrentIndex(0)

    run_button.clicked.connect(handle_test_execution)
    back_button.clicked.connect(handle_back)

    return outer


class TestRunnerThread(QThread):
    finished = pyqtSignal(int)
    progress_updated = pyqtSignal(int, str)
    log_updated = pyqtSignal(str)

    def __init__(self, cmd, cwd, env, log_path):
        super().__init__()
        self.cmd = cmd
        self.cwd = cwd
        self.env = env
        self.log_path = log_path

    def run(self):
        import subprocess
        p = subprocess.Popen(
        self.cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=self.cwd,
        env=self.env,
        text=True,
        encoding="utf-8",  # ✅ 強制使用 utf-8 解碼
        bufsize=1
            )

        with open(self.log_path, "w", encoding="utf-8") as logfile:
            for line in iter(p.stdout.readline, ''):
                logfile.write(line)
                logfile.flush()
                self.log_updated.emit(line.strip())

                if line.startswith("[PROGRESS]"):
                    parts = line.strip().split(" ", 2)
                    try:
                        percent = int(parts[1])
                        step = parts[2] if len(parts) > 2 else ""
                        self.progress_updated.emit(percent, step)
                    except:
                        pass

        self.finished.emit(p.wait())