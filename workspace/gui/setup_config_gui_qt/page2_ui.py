from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit,
    QVBoxLayout, QHBoxLayout, QMessageBox, QProgressBar,
    QCheckBox, QFileDialog, QApplication, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from datetime import datetime
from pathlib import Path
import sys, os

from workspace.gui.controller.report_controller import open_report
from workspace.gui.setup_config_gui_qt.validator import load_user_config
from workspace.config.setup_config.config_writer import update_env
from workspace.gui.setup_config_gui_qt.test_runner_thread import TestRunnerThread

def create_test_page(stack_widget):
    outer = QWidget()
    main_layout = QVBoxLayout()

    config = load_user_config()
    pfid = config.get("PF_ID", "未設定")
    key = config.get("PRIVATE_KEY", "未設定")
    rule = config.get("BET_AMOUNT_RULE", "未設定")
    level = config.get("BET_LEVEL_MODE", "未設定")
    debug_ws_packet = config.get("DEBUG_WS_PACKET", "false")

    level_display = {
        "min": "最小限紅模式",
        "max": "最大限紅模式"
    }.get(level, "未設定")

    # Group 1: 測試設定資訊
    config_group = QGroupBox("測試環境設定")
    config_layout = QGridLayout()
    config_layout.addWidget(QLabel("帳號 (PF_ID)："), 0, 0)
    config_layout.addWidget(QLabel(pfid), 0, 1)
    config_layout.addWidget(QLabel("金鑰 (PRIVATE_KEY)："), 1, 0)
    config_layout.addWidget(QLabel(key), 1, 1)
    config_layout.addWidget(QLabel("下注金額規則："), 2, 0)
    config_layout.addWidget(QLabel(rule or "未設定"), 2, 1)
    config_layout.addWidget(QLabel("限紅模式："), 3, 0)
    config_layout.addWidget(QLabel(level_display), 3, 1)
    config_group.setLayout(config_layout)
    main_layout.addWidget(config_group)

    # Group 2: 控制區
    control_group = QGroupBox("測試選擇與啟動")
    control_layout = QVBoxLayout()

    type_layout = QHBoxLayout()
    type_layout.addWidget(QLabel("選擇測試流程："))
    test_type_combo = QComboBox()
    test_type_combo.addItems(["type_1", "type_2", "type_3", "ALL"])
    type_layout.addWidget(test_type_combo)

    debug_checkbox = QCheckBox("啟用 DEBUG 模式（封包紀錄）")
    debug_checkbox.setChecked(debug_ws_packet.lower() == "true")
    type_layout.addWidget(debug_checkbox)
    control_layout.addLayout(type_layout)

    progress_bar = QProgressBar()
    progress_bar.setValue(0)
    progress_bar.setFormat("尚未開始")
    control_layout.addWidget(progress_bar)

    # 動圖（隱藏預設）
    loading_gif = QLabel()
    movie = QMovie("workspace/assets/loading.gif")  # 放在專案 assets 目錄下
    loading_gif.setMovie(movie)
    loading_gif.setVisible(False)
    control_layout.addWidget(loading_gif)

    control_group.setLayout(control_layout)
    main_layout.addWidget(control_group)

    # Group 3: 輸出區
    output_group = QGroupBox("執行輸出")
    output_layout = QVBoxLayout()
    result_output = QTextEdit()
    result_output.setReadOnly(True)
    result_output.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc;")
    output_layout.addWidget(result_output)
    output_group.setLayout(output_layout)
    main_layout.addWidget(output_group)

    # 控制按鈕
    export_log_button = QPushButton("匯出執行記錄")
    export_log_button.setEnabled(False)
    run_button = QPushButton("執行測試")
    back_button = QPushButton("返回上一頁")
    view_report_button = QPushButton("查看測試報表")
    view_report_button.setEnabled(False)

    btn_layout = QHBoxLayout()
    for btn in [run_button, back_button, view_report_button, export_log_button]:
        btn_layout.addWidget(btn)
    main_layout.addLayout(btn_layout)

    outer.setLayout(main_layout)

    def on_test_finished(code, selected_type):
        for btn in [run_button, back_button, test_type_combo]:
            btn.setEnabled(True)
        run_button.setText("執行測試")
        view_report_button.setEnabled(True)
        export_log_button.setEnabled(True)
        QApplication.restoreOverrideCursor()
        loading_gif.setVisible(False)
        movie.stop()

        if code == 0:
            QMessageBox.information(None, "完成", f"✅ 測試 {selected_type} 完成！")
        else:
            QMessageBox.warning(None, "錯誤", f"❌ 測試 {selected_type} 執行失敗，請查看輸出內容")

    def handle_test_execution():
        selected_type = test_type_combo.currentText()
        if not selected_type:
            QMessageBox.warning(None, "錯誤", "請選擇要執行的測試類型")
            return

        result_output.clear()
        progress_bar.setValue(0)
        progress_bar.setFormat("尚未開始")
        for btn in [view_report_button, export_log_button]:
            btn.setEnabled(False)

        update_env("DEBUG_WS_PACKET", "true" if debug_checkbox.isChecked() else "false")
        for btn in [run_button, back_button, test_type_combo]:
            btn.setEnabled(False)
        run_button.setText("執行中...")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        loading_gif.setVisible(True)
        movie.start()

        task_arg = "001+009"
        main_path = Path(__file__).resolve().parents[3] / "main.py"
        log_path = main_path.parent / "last_test.log"

        env = os.environ.copy()
        env["PYTHONPATH"] = str(main_path.parent)
        env["PYTHONIOENCODING"] = "utf-8"

        cmd = [sys.executable, str(main_path), "--task", task_arg, "--type", selected_type]

        outer.thread = TestRunnerThread(cmd, str(main_path.parent), env, log_path)
        outer.thread.progress_updated.connect(lambda p, s: (
            progress_bar.setValue(p),
            progress_bar.setFormat(f"{s} (%p%)")
        ))
        outer.thread.log_updated.connect(lambda line: result_output.append(line))
        outer.thread.finished.connect(lambda code: on_test_finished(code, selected_type))
        outer.thread.start()

    def handle_export_log():
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"log_{now}.txt"
        file_path, _ = QFileDialog.getSaveFileName(None, "匯出執行記錄", default_name, "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result_output.toPlainText())
            QMessageBox.information(None, "成功", "✅ 執行記錄已成功匯出！")

    run_button.clicked.connect(handle_test_execution)
    back_button.clicked.connect(lambda: stack_widget.setCurrentIndex(0))
    view_report_button.clicked.connect(open_report)
    export_log_button.clicked.connect(handle_export_log)

    return outer