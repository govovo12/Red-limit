from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication
from workspace.gui.setup_config_gui_qt.validator import load_user_config
from workspace.config.setup_config.config_writer import update_env


def render_config_text(ui):
    config = load_user_config()
    pfid = config.get("PF_ID", "未設定")
    key = config.get("PRIVATE_KEY", "未設定")
    rule = config.get("BET_AMOUNT_RULE", "未設定")
    level = config.get("BET_LEVEL_MODE", "未設定")
    debug_ws = config.get("DEBUG_WS_PACKET", "false")

    level_display = {"min": "最小限紅模式", "max": "最大限紅模式"}.get(level, "未設定")

    config_text = f"""帳號（PF_ID）：{pfid}
金鑰（PRIVATE_KEY）：{key}
下注金額限制：{rule}
限紅模式：{level_display}"""

    is_valid = all(v not in ["", "未設定"] for v in [pfid, key, rule, level])

    ui["config_output"].setPlainText(config_text)
    ui["debug_checkbox"].setChecked(debug_ws.lower() == "true")

    ui["status_label"].setText(
        "✅ 設定已成功載入" if is_valid else "❌ 尚未完整設定，請確認各欄位"
    )
    ui["status_label"].setStyleSheet(f"color: {'green' if is_valid else 'red'}; font-weight: bold")

    # 調整輸出框高度（延後處理，確保 layout 完成）
    QTimer.singleShot(0, lambda: _adjust_output_height(ui["config_output"]))


def _adjust_output_height(text_edit):
    doc_height = text_edit.document().size().height()
    line_height = text_edit.fontMetrics().height()
    total = int(doc_height + line_height + 20)
    text_edit.setFixedHeight(max(total, 96))


def copy_config_to_clipboard(ui):
    text = ui["config_output"].toPlainText()
    QApplication.clipboard().setText(text)


def update_debug_env_from_checkbox(ui):
    enabled = ui["debug_checkbox"].isChecked()
    update_env("DEBUG_WS_PACKET", "true" if enabled else "false")


def toggle_controls_enabled(ui, enabled: bool):
    ui["run_button"].setEnabled(enabled)
    ui["back_button"].setEnabled(enabled)
    ui["test_type_combo"].setEnabled(enabled)


def set_progress(ui, percent: int, message: str):
    ui["progress_bar"].setValue(percent)
    ui["progress_bar"].setFormat(f"{message} (%p%)")


def append_result_log(ui, line: str):
    ui["result_output"].append(line)
    cursor = ui["result_output"].textCursor()
    cursor.movePosition(QTextCursor.End)
    ui["result_output"].setTextCursor(cursor)


def show_loading(ui, enabled: bool):
    ui["loading_gif"].setVisible(enabled)
    if enabled:
        ui["movie"].start()
    else:
        ui["movie"].stop()
