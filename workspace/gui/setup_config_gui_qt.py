import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))  # 加入 Red-limit/ 作為根路徑

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton,
    QHBoxLayout, QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import subprocess

from workspace.config.setup_config.input_validator import (
    validate_pf_id, validate_private_key
)
from workspace.config.setup_config.config_writer import save_env_config
from workspace.tools.common.result_code import ResultCode


class LimitConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("限紅測試初始化工具")
        self.setFixedSize(500, 400)

        # ✅ 使用者是否觸碰過欄位
        self.touched_pfid = False
        self.touched_key = False
        self.touched_rule_val = False

        self.init_ui()

    def init_ui(self):
        font_label = QFont("Microsoft JhengHei", 10)
        font_err = QFont("Microsoft JhengHei", 9)
        font_err.setItalic(True)

        self.pfid_label = QLabel("PF_ID")
        self.pfid_input = QLineEdit()
        self.pfid_input.setPlaceholderText("請輸入 PF_ID")
        self.pfid_input.textChanged.connect(lambda: self.on_input("pfid"))
        self.pfid_err = QLabel("")
        self.pfid_err.setFont(font_err)
        self.pfid_err.setStyleSheet("color: red")

        self.key_label = QLabel("PRIVATE_KEY")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("請輸入 32 碼金鑰")
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.textChanged.connect(lambda: self.on_input("key"))
        self.key_err = QLabel("")
        self.key_err.setFont(font_err)
        self.key_err.setStyleSheet("color: red")

        self.mode_label = QLabel("限紅邏輯模式")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["最大限紅", "最小限紅"])

        self.rule_label = QLabel("限紅規則運算")
        self.rule_combo = QComboBox()
        self.rule_combo.addItems([">=", "<=", "==", ">", "<"])
        self.rule_combo.currentIndexChanged.connect(self.validate_all_fields)
        self.rule_value = QLineEdit()
        self.rule_value.setPlaceholderText("數值")
        self.rule_value.textChanged.connect(lambda: self.on_input("rule_val"))
        self.rule_err = QLabel("")
        self.rule_err.setFont(font_err)
        self.rule_err.setStyleSheet("color: red")
        rule_layout = QHBoxLayout()
        rule_layout.addWidget(self.rule_combo)
        rule_layout.addWidget(self.rule_value)

        self.submit_btn = QPushButton("送出設定 ✅")
        self.submit_btn.setEnabled(False)
        self.submit_btn.clicked.connect(self.on_submit)
        self.exit_btn = QPushButton("結束")
        self.exit_btn.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("🎮 限紅測試初始化工具", alignment=Qt.AlignCenter))
        layout.addWidget(self.pfid_label)
        layout.addWidget(self.pfid_input)
        layout.addWidget(self.pfid_err)
        layout.addWidget(self.key_label)
        layout.addWidget(self.key_input)
        layout.addWidget(self.key_err)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.mode_combo)
        layout.addWidget(self.rule_label)
        layout.addLayout(rule_layout)
        layout.addWidget(self.rule_err)
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.exit_btn)
        layout.addStretch()

        self.setLayout(layout)

    def on_input(self, field):
        if field == "pfid":
            self.touched_pfid = True
        elif field == "key":
            self.touched_key = True
        elif field == "rule_val":
            self.touched_rule_val = True
        self.validate_all_fields()

    def validate_all_fields(self):
        pfid = self.pfid_input.text().strip()
        key = self.key_input.text().strip()
        rule_val = self.rule_value.text().strip()
        valid = True

        _, code = validate_pf_id(pfid)
        if code != ResultCode.SUCCESS and self.touched_pfid:
            self.pfid_err.setText("格式錯誤：需含底線，僅限英數字")
            valid = False
        else:
            self.pfid_err.setText("")

        _, code = validate_private_key(key)
        if code != ResultCode.SUCCESS and self.touched_key:
            self.key_err.setText("金鑰錯誤：32 碼英數字")
            valid = False
        else:
            self.key_err.setText("")

        try:
            float(rule_val)
            self.rule_err.setText("")
        except ValueError:
            if self.touched_rule_val:
                self.rule_err.setText("請輸入有效數值")
            valid = False

        self.submit_btn.setEnabled(valid)

    def on_submit(self):
        pfid = self.pfid_input.text().strip()
        key = self.key_input.text().strip()
        mode_text = self.mode_combo.currentText()
        rule_symbol = self.rule_combo.currentText()
        rule_val = self.rule_value.text().strip()

        bet_mode = "max" if "最大" in mode_text else "min"
        bet_rule = f"{rule_symbol}{rule_val}"

        data = {
            "PF_ID": pfid,
            "PRIVATE_KEY": key,
            "BET_LEVEL_MODE": bet_mode,
            "BET_AMOUNT_RULE": bet_rule,
        }

        code = save_env_config(data)
        if code != ResultCode.SUCCESS:
            QMessageBox.critical(self, "錯誤", "❌ 寫入 .env.user 失敗")
            return

        # ✅ 顯示完整寫入位置
        env_path = Path(__file__).resolve().parents[2] / ".env.user"
        try:
            subprocess.Popen([
                "python",
                "workspace/config/setup_config/subcontrollers/setup_config_controller.py"
            ])
            QMessageBox.information(
                self, "成功",
                f"✅ 設定成功\n\n已寫入：\n{env_path}"
            )
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"❌ 主控執行失敗：{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LimitConfigWindow()
    window.show()
    sys.exit(app.exec_())
