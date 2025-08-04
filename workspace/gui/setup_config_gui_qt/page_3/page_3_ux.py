from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication
from workspace.tools.env.tools_env_user_loader import load_user_config
from workspace.tools.env.env_writer import update_env
from PyQt5.QtCore import QTimer, QPoint

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
    ui["status_label"].setStyleSheet(
        "color: green; font-size: 13px; font-weight: bold;" if is_valid
        else "color: red; font-size: 13px; font-weight: bold;"
    )


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
    ui["progress_status_label"].setText(f"{message} ({percent}%)")

    def move_sheep_safely():
        sheep = ui["loading_gif"]
        bar = ui["progress_bar"]

        if bar.width() <= 5:
            QTimer.singleShot(50, move_sheep_safely)
            return

        bar_width = bar.width()
        sheep_width = sheep.width()

        # 🧠 用進度條實際寬度作基準
        sheep_x = int(bar_width * percent / 100 - sheep_width / 2)
        sheep_x = max(0, min(sheep_x, bar_width - sheep_width))

        # ⚠️ 綿羊所在的 overlay 是在 progress_area 下方，位置必須是絕對的
        sheep.move(sheep_x, 0)

    QTimer.singleShot(0, move_sheep_safely)




def append_result_log(ui, line: str):
    output = ui["result_output"]
    cursor = output.textCursor()

    # 🔒 記錄原本 scroll bar 狀態
    vertical_scroll = output.verticalScrollBar().value()
    horizontal_scroll = output.horizontalScrollBar().value()

    output.append(line)

    # 🧠 強制游標移到底部但不要水平偏移
    cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
    output.setTextCursor(cursor)

    # ✅ 恢復原本橫向位置，避免右滑
    output.horizontalScrollBar().setValue(horizontal_scroll)


def show_loading(ui, enabled: bool):
    ui["loading_gif"].setVisible(enabled)
    if enabled:
        ui["movie"].start()
        ui["loading_gif"].move(0, 0)  # ✅ 每次啟動時 reset 為最左
    else:
        ui["movie"].stop()



def setup_page3_logic(ui, stack_widget):
    ui["back_button"].clicked.connect(lambda: stack_widget.setCurrentIndex(1))
    ui["copy_btn"].clicked.connect(lambda: copy_config_to_clipboard(ui))
    ui["debug_checkbox"].stateChanged.connect(lambda: update_debug_env_from_checkbox(ui))
