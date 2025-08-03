import sys, os
from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog

from workspace.gui.setup_config_gui_qt.page_3.page_3_ui import build_page_3_ui
from workspace.gui.setup_config_gui_qt.page_3.page_3_ux import (
    render_config_text, copy_config_to_clipboard, update_debug_env_from_checkbox,
    toggle_controls_enabled, show_loading, set_progress, append_result_log,
    setup_page3_logic  # ✅ 新增：統一行為綁定
)
from workspace.gui.controller.report_controller import open_report
from workspace.gui.setup_config_gui_qt.modules.test_runner_thread import TestRunnerThread
from workspace.config.paths import ROOT_DIR

def create_page_3(stack_widget):
    ui = build_page_3_ui()
    setup_page3_logic(ui, stack_widget)  # ✅ UX 行為初始化

    def go_to_page3():
        render_config_text(ui)  # ✅ 每次切換都重新載入設定
        ui["progress_status_label"].setText("尚未開始")  # ✅ 初始化進度字幕
        stack_widget.setCurrentIndex(2)  # Page3 在 index 2

    def handle_run():
        selected_type = ui["test_type_combo"].currentText()
        if not selected_type:
            QMessageBox.warning(None, "錯誤", "請選擇要執行的測試類型")
            return

        ui["result_output"].clear()
        ui["progress_bar"].setValue(0)
        ui["progress_bar"].setFormat("")
        ui["view_report_button"].setEnabled(False)
        ui["export_log_button"].setEnabled(False)

        update_debug_env_from_checkbox(ui)
        toggle_controls_enabled(ui, False)
        ui["run_button"].setText("執行中...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        show_loading(ui, True)

        task_arg = "001+009"
        main_path = ROOT_DIR / "main.py"

        if not main_path.exists():
            QMessageBox.critical(None, "找不到 main.py", f"❌ 無法找到 main.py\n實際路徑：{main_path}")
            return

        log_path = main_path.parent / "last_test.log"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(main_path.parent)
        env["PYTHONIOENCODING"] = "utf-8"

        cmd = [sys.executable, str(main_path), "--task", task_arg, "--type", selected_type]

        ui["widget"].thread = TestRunnerThread(cmd, str(main_path.parent), env, log_path)
        ui["widget"].thread.progress_updated.connect(lambda p, s: set_progress(ui, p, s))
        ui["widget"].thread.log_updated.connect(lambda line: append_result_log(ui, line))
        ui["widget"].thread.finished.connect(lambda code: handle_finish(code, selected_type))
        ui["widget"].thread.start()

    def handle_finish(code: int, selected_type: str):
        toggle_controls_enabled(ui, True)
        ui["run_button"].setText("執行測試")
        QApplication.restoreOverrideCursor()
        show_loading(ui, False)
        ui["view_report_button"].setEnabled(True)
        ui["export_log_button"].setEnabled(True)

        if code == 0:
            QMessageBox.information(None, "完成", f"✅ 測試 {selected_type} 完成！")
        else:
            QMessageBox.warning(None, "錯誤", f"❌ 測試 {selected_type} 執行失敗")

    def handle_export_log():
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"log_{now}.txt"
        file_path, _ = QFileDialog.getSaveFileName(None, "匯出執行記錄", default_name, "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(ui["result_output"].toPlainText())
            QMessageBox.information(None, "成功", "✅ 執行記錄已成功匯出！")

    ui["run_button"].clicked.connect(handle_run)
    ui["view_report_button"].clicked.connect(open_report)
    ui["export_log_button"].clicked.connect(handle_export_log)
    ui["copy_btn"].clicked.connect(lambda: copy_config_to_clipboard(ui))

    return ui["widget"], go_to_page3  # ✅ 新增：回傳切換函式


