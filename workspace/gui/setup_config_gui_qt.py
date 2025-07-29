import sys
from pathlib import Path
import os
import subprocess

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))  # ✅ 加入 Red-limit 為 PYTHONPATH

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton,
    QHBoxLayout, QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from workspace.config.setup_config.input_validator import (
    validate_pf_id, validate_private_key
)
from workspace.config.setup_config.config_writer import save_env_config
from workspace.tools.common.result_code import ResultCode


# === 建構元件 ===
def create_label(text):
    return QLabel(text)


def create_error_label():
    font = QFont("Microsoft JhengHei", 9)
    font.setItalic(True)
    label = QLabel("")
    label.setFont(font)
    label.setStyleSheet("color: red")
    return label


def create_combo(items):
    combo = QComboBox()
    combo.addItems(items)
    return combo


# === 欄位驗證 ===
def validate_fields(pfid_input, key_input, rule_input,
                    pfid_err, key_err, rule_err, submit_btn):
    pfid = pfid_input.text().strip()
    key = key_input.text().strip()
    rule_val = rule_input.text().strip()
    valid = True

    _, code = validate_pf_id(pfid)
    if code != ResultCode.SUCCESS:
        pfid_err.setText("格式錯誤：需含底線，僅限英數字")
        valid = False
    else:
        pfid_err.setText("")

    _, code = validate_private_key(key)
    if code != ResultCode.SUCCESS:
        key_err.setText("金鑰錯誤：32 碼英數字")
        valid = False
    else:
        key_err.setText("")

    try:
        float(rule_val)
        rule_err.setText("")
    except ValueError:
        rule_err.setText("請輸入有效數值")
        valid = False

    submit_btn.setEnabled(valid)


# === 提交處理 ===
def handle_submit(pfid_input, key_input, mode_combo, rule_combo, rule_input, parent_window):
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

    # ✅ 等待 .env.user 寫入完成
    import time
    root_dir = str(Path(__file__).resolve().parents[2])
    env_path = Path(root_dir) / ".env.user"
    wait_time = 0
    while not env_path.exists() and wait_time < 2.0:
        time.sleep(0.1)
        wait_time += 0.1

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = root_dir
        env["LIMIT_SETUP_MODE"] = "auto"  # ✅ 必須設定

        subprocess.Popen(
            [sys.executable, "workspace/config/setup_config/subcontrollers/setup_config_controller.py"],
            cwd=root_dir,
            env=env
        )

        QMessageBox.information(
            parent_window, "成功",
            f"✅ 設定成功\\n\\n已寫入：\\n{env_path}"
        )
        parent_window.close()
    except Exception as e:
        QMessageBox.critical(parent_window, "錯誤", f"❌ 主控執行失敗：{e}")




# === 主 GUI 流程 ===
def main():
    app = QApplication(sys.argv)
    win = QWidget()
    win.setWindowTitle("限紅測試初始化工具")
    win.setFixedSize(500, 400)

    layout = QVBoxLayout()
    layout.addWidget(QLabel("🎮 限紅測試初始化工具", alignment=Qt.AlignCenter))

    # PF_ID
    pfid_label = create_label("PF_ID")
    pfid_input = QLineEdit()
    pfid_input.setPlaceholderText("請輸入 PF_ID")
    pfid_err = create_error_label()

    # PRIVATE_KEY
    key_label = create_label("PRIVATE_KEY")
    key_input = QLineEdit()
    key_input.setPlaceholderText("請輸入 32 碼金鑰")
    key_input.setEchoMode(QLineEdit.Password)
    key_err = create_error_label()

    # MODE + RULE
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

    # Buttons
    submit_btn = QPushButton("送出設定 ✅")
    submit_btn.setEnabled(False)

    exit_btn = QPushButton("結束")
    exit_btn.clicked.connect(win.close)

    # 加入元件
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
    layout.addWidget(submit_btn)
    layout.addWidget(exit_btn)
    layout.addStretch()

    # 綁定驗證事件
    pfid_input.textChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))
    key_input.textChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))
    rule_input.textChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))
    rule_combo.currentIndexChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))

    submit_btn.clicked.connect(lambda: handle_submit(pfid_input, key_input, mode_combo, rule_combo, rule_input, win))

    win.setLayout(layout)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
