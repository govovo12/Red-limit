import os
import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit,
    QVBoxLayout, QHBoxLayout, QProgressDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from workspace.gui.setup_config_gui_qt.validator import load_user_config
from workspace.gui.setup_config_gui_qt.progress_watcher import show_progress_dialog


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
        f"下注等級模式：{level_display}"
    ]

    config_label = QLabel("\n".join(lines))
    config_label.setStyleSheet("font-size: 14px;")
    layout.addWidget(config_label)

    # 測試類型選單
    type_label = QLabel("請選擇要執行的測試流程：")
    layout.addWidget(type_label)

    test_type_combo = QComboBox()
    test_type_combo.addItems(["type_1", "type_2", "type_3"])
    layout.addWidget(test_type_combo)

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

    def on_test_finished(code, progress, log_path, selected_type):
        progress.close()
        try:
            result = Path(log_path).read_text(encoding="utf-8")
        except Exception as e:
            result = f"❌ 無法讀取結果檔案\n{e}"

        result_output.setPlainText(result)
        if code == 0:
            QMessageBox.information(None, "完成", f"✅ 測試 {selected_type} 完成！")
        else:
            QMessageBox.warning(None, "錯誤", f"❌ 測試 {selected_type} 執行失敗，請查看輸出內容")

    def handle_test_execution():
        selected_type = test_type_combo.currentText()
        if not selected_type:
            QMessageBox.warning(None, "錯誤", "請選擇要執行的測試類型")
            return

        task_arg = "001+009"
        main_path = Path(__file__).resolve().parents[3] / "main.py"
        log_path = main_path.parent / "last_test.log"

        env = os.environ.copy()
        env["PYTHONPATH"] = str(main_path.parent)
        env["PYTHONIOENCODING"] = "utf-8"

        cmd = [sys.executable, str(main_path), "--task", task_arg, "--type", selected_type]

        # ✅ 顯示進度條視窗（會即時讀取 .progress.json）
        progress = show_progress_dialog()

        outer.thread = TestRunnerThread(cmd, str(main_path.parent), env, log_path)
        outer.thread.finished.connect(lambda code: on_test_finished(code, progress, log_path, selected_type))
        outer.thread.start()

    def handle_back():
        stack_widget.setCurrentIndex(0)

    run_button.clicked.connect(handle_test_execution)
    back_button.clicked.connect(handle_back)

    return outer


class TestRunnerThread(QThread):
    finished = pyqtSignal(int)

    def __init__(self, cmd, cwd, env, log_path):
        super().__init__()
        self.cmd = cmd
        self.cwd = cwd
        self.env = env
        self.log_path = log_path

    def run(self):
        import subprocess
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        with open(self.log_path, "w", encoding="utf-8") as f:
            process = subprocess.Popen(
                self.cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                cwd=self.cwd,
                env=self.env,
                creationflags=creationflags
            )
            process.wait()
            self.finished.emit(process.returncode)
