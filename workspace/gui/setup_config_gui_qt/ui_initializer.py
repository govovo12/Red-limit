from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt

import os
import sys
import time
import subprocess
from pathlib import Path

from workspace.config.setup_config.config_writer import save_env_config
from workspace.tools.common.result_code import ResultCode
from workspace.gui.setup_config_gui_qt.validator import validate_fields


# === 小元件建構 ===
def create_label(text):
    return QLabel(text)

def create_error_label():
    label = QLabel("")
    label.setStyleSheet("color: red")
    return label

def create_combo(items):
    combo = QComboBox()
    combo.addItems(items)
    return combo


# === 初始化表單頁 ===
def create_page1(stacked):
    page = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(QLabel("🎮 限紅測試初始化工具", alignment=Qt.AlignCenter))

    pfid_label = create_label("PF_ID")
    pfid_input = QLineEdit()
    pfid_input.setPlaceholderText("請輸入 PF_ID")
    pfid_err = create_error_label()

    key_label = create_label("PRIVATE_KEY")
    key_input = QLineEdit()
    key_input.setPlaceholderText("請輸入 32 碼金鑰")
    key_input.setEchoMode(QLineEdit.Password)
    key_err = create_error_label()

    mode_label = create_label("限紅邏輯模式")
    mode_combo = create_combo(["最大限紅", "最小限紅"])

    rule_label = create_label("限紅規則運算")
    rule_combo = create_combo([">=", "<=", "==", ">", "<"])
    rule_input = QLineEdit()
    rule_input.setPlaceholderText("數值")
    rule_err = create_error_label()

    rule_layout = QHBoxLayout()
    rule_layout.addWidget(rule_combo)
    rule_layout.addWidget(rule_input)

    submit_btn = QPushButton("送出設定 ✅")
    submit_btn.setEnabled(False)
    skip_btn = QPushButton("跳過設定 ➤")
    skip_btn.clicked.connect(lambda: stacked.setCurrentIndex(1))

    layout.addWidget(pfid_label)
    layout.addWidget(pfid_input)
    layout.addWidget(pfid_err)
    layout.addWidget(key_label)
    layout.addWidget(key_input)
    layout.addWidget(key_err)
    layout.addWidget(mode_label)
    layout.addWidget(mode_combo)
    layout.addWidget(rule_label)
    layout.addLayout(rule_layout)
    layout.addWidget(rule_err)

    btns = QHBoxLayout()
    btns.addWidget(submit_btn)
    btns.addWidget(skip_btn)
    layout.addLayout(btns)
    layout.addStretch()

    page.setLayout(layout)

    pfid_input.textChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))
    key_input.textChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))
    rule_input.textChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))
    rule_combo.currentIndexChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))

    submit_btn.clicked.connect(lambda: handle_submit(pfid_input, key_input, mode_combo, rule_combo, rule_input, page, stacked))
    return page


def handle_submit(pfid_input, key_input, mode_combo, rule_combo, rule_input, parent_window, stacked):
    pfid = pfid_input.text().strip()
    key = key_input.text().strip()
    mode = mode_combo.currentText()
    rule = f"{rule_combo.currentText()}{rule_input.text().strip()}"

    data = {
        "PF_ID": pfid,
        "PRIVATE_KEY": key,
        "BET_LEVEL_MODE": "max" if "最大" in mode else "min",
        "BET_AMOUNT_RULE": rule,
    }

    code = save_env_config(data)
    if code != ResultCode.SUCCESS:
        QMessageBox.critical(parent_window, "錯誤", "❌ 寫入 .env.user 失敗")
        return

    root_dir = str(Path(__file__).resolve().parents[3])
    env_path = Path(root_dir) / ".env.user"
    wait_time = 0
    while not env_path.exists() and wait_time < 2.0:
        time.sleep(0.1)
        wait_time += 0.1

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = root_dir
        env["LIMIT_SETUP_MODE"] = "auto"

        subprocess.Popen(
            [sys.executable, "workspace/config/setup_config/subcontrollers/setup_config_controller.py"],
            cwd=root_dir,
            env=env
        )

        QMessageBox.information(
            parent_window, "成功",
            f"✅ 設定成功\n\n已寫入：\n{env_path}"
        )
        stacked.setCurrentIndex(1)
    except Exception as e:
        QMessageBox.critical(parent_window, "錯誤", f"❌ 主控執行失敗：{e}")
