import os
import sys
import time
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox
from workspace.config.setup_config.config_writer import save_env_config
from workspace.tools.common.result_code import ResultCode
from workspace.gui.setup_config_gui_qt.validator import validate_fields


def setup_page2_logic(widgets, stack_widget):
    pfid_input = widgets["pfid_input"]
    key_input = widgets["key_input"]
    rule_input = widgets["rule_input"]
    pfid_err = widgets["pfid_err"]
    key_err = widgets["key_err"]
    rule_err = widgets["rule_err"]
    submit_btn = widgets["submit_btn"]
    skip_btn = widgets["skip_btn"]
    page = widgets["page"]
    mode_combo = widgets["mode_combo"]
    rule_combo = widgets["rule_combo"]

    # 驗證欄位連動
    pfid_input.textChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))
    key_input.textChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))
    rule_input.textChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))
    rule_combo.currentIndexChanged.connect(lambda: validate_fields(pfid_input, key_input, rule_input, pfid_err, key_err, rule_err, submit_btn))

    def handle_submit():
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
            QMessageBox.critical(page, "錯誤", "❌ 寫入 .env.user 失敗")
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
                page, "成功",
                f"✅ 設定成功\n\n已寫入：\n{env_path}"
            )
            stack_widget.setCurrentIndex(1)
        except Exception as e:
            QMessageBox.critical(page, "錯誤", f"❌ 主控執行失敗：{e}")

    submit_btn.clicked.connect(handle_submit)
    skip_btn.clicked.connect(lambda: stack_widget.setCurrentIndex(1))
