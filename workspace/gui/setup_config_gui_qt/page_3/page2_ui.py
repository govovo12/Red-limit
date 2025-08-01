from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit,
    QVBoxLayout, QHBoxLayout, QMessageBox, QProgressBar,
    QCheckBox, QFileDialog, QApplication, QGroupBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QFont
from datetime import datetime
from pathlib import Path
import sys, os

from workspace.gui.controller.report_controller import open_report
from workspace.gui.setup_config_gui_qt.validator import load_user_config
from workspace.config.setup_config.config_writer import update_env
from workspace.gui.setup_config_gui_qt.test_runner_thread import TestRunnerThread
from PyQt5.QtWidgets import QFrame 

def create_test_page(stack_widget):
    outer = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(16, 16, 16, 16)
    main_layout.setSpacing(4)

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

    # ✅ CLI-style 顯示區塊（完整排版）
    config_frame = QFrame()
    config_frame.setFrameShape(QFrame.StyledPanel)
    config_frame.setStyleSheet("""
        QFrame {
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px;
        }
    """)

    config_layout = QVBoxLayout()
    config_layout.setSpacing(6)
    config_layout.setContentsMargins(8, 8, 8, 8)

    # 標題 + 📋 同排
    title_layout = QHBoxLayout()
    group_title = QLabel("測試環境設定")
    group_title.setFont(QFont("Microsoft JhengHei", 11, QFont.Bold))
    group_title.setStyleSheet("color: #2c3e50;")
    copy_btn = QPushButton("📋")
    copy_btn.setToolTip("複製全部設定內容")
    copy_btn.setFixedSize(24, 24)
    copy_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    title_layout.addWidget(group_title)
    title_layout.addStretch()
    title_layout.addWidget(copy_btn)
    config_layout.addLayout(title_layout)

    # CLI-style 設定內容
    config_text = f"""帳號（PF_ID）：{pfid}
金鑰（PRIVATE_KEY）：{key}
下注金額限制：{rule}
限紅模式：{level_display}"""

    from PyQt5.QtCore import QTimer

    config_output = QTextEdit()
    config_output.setReadOnly(True)
    config_output.setStyleSheet("background-color: #fefefe; border: 1px solid #ddd;")
    config_output.setText(config_text)
    config_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    config_output.setMinimumHeight(96)  # 保底顯示至少 4 行

    def adjust_config_output_height():
        document_height = config_output.document().size().height()
        line_height = config_output.fontMetrics().height()
        padding = 20
        total_height = int(document_height + line_height + padding)
        if total_height < 60:
            total_height = 96
        config_output.setFixedHeight(total_height)

    # ✅ 延後呼叫（確保 layout 結束才調整）
    QTimer.singleShot(0, adjust_config_output_height)

    # ✅ 加入畫面（這行不能省）
    config_layout.addWidget(config_output)

    # 複製功能
    copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(config_output.toPlainText()))

    # 狀態提示
    status_label = QLabel(
        "✅ 設定已成功載入" if all(v not in ["", "未設定"] for v in [pfid, key, rule, level])
        else "❌ 尚未完整設定，請確認各欄位"
    )
    status_label.setFont(QFont("Microsoft JhengHei", 10))
    status_label.setStyleSheet(f"color: {'green' if all(v not in ['未設定'] for v in [pfid, key, rule, level]) else 'red'}; font-weight: bold")
    status_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    status_label.setWordWrap(False)
    status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    config_layout.addWidget(status_label)

    config_frame.setLayout(config_layout)
    main_layout.addWidget(config_frame)

    # Group 2: 控制區
    control_group = QGroupBox("測試選擇與啟動")
    control_group.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px;
        }
    """)
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
    progress_bar.setFixedHeight(18)
    control_layout.addWidget(progress_bar)

    loading_gif = QLabel()
    movie = QMovie("workspace/assets/loading.gif")
    loading_gif.setMovie(movie)
    loading_gif.setVisible(False)
    control_layout.addWidget(loading_gif)

    control_group.setLayout(control_layout)
    main_layout.addWidget(control_group)

    # Group 3: 輸出區
    output_group = QGroupBox("執行輸出")
    output_group.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 4px;
        }
    """)
    output_layout = QVBoxLayout()
    result_output = QTextEdit()
    result_output.setReadOnly(True)
    result_output.setLineWrapMode(QTextEdit.NoWrap)  # 可選：不自動換行
    result_output.setStyleSheet("""
    QTextEdit {
        background-color: #000000;
        color: #00FF00;
        font-family: Consolas, Courier, monospace;
        font-size: 13px;
        border: none;
    }
""")
    output_layout.addWidget(result_output)
    output_group.setLayout(output_layout)
    output_group.setMinimumHeight(150)
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