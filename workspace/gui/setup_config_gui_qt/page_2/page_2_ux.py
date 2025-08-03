from PyQt5.QtWidgets import QMessageBox
from workspace.tools.env.env_writer import save_env_config
from workspace.tools.common.result_code import ResultCode

def handle_submit(ui, stack_widget, go_to_page3) -> None:
    """
    UX 層：處理使用者填完資料按下「送出設定」後的行為。
    - 驗證資料
    - 寫入 .env.user
    - 顯示成功 / 錯誤訊息
    - ✅ 成功後點 OK 再切頁（改為呼叫 Page3 控制器提供的 go_to_page3）
    """
    pfid_input = ui["pfid_input"]
    key_input = ui["key_input"]
    mode_combo = ui["mode_combo"]
    rule_combo = ui["rule_combo"]
    rule_input = ui["rule_input"]
    page = ui["page"]

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
        QMessageBox.critical(page, "錯誤", "❌ 寫入設定檔失敗")
        return

    msg_box = QMessageBox(page)
    msg_box.setWindowTitle("成功")
    msg_box.setText("✅ 寫入設定檔成功")
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setStandardButtons(QMessageBox.Ok)
    ret = msg_box.exec_()

    if ret == QMessageBox.Ok:
        go_to_page3()  # ✅ 改為呼叫 Page3 提供的函式
