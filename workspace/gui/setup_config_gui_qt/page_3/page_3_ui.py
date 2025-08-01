from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit, QVBoxLayout,
    QHBoxLayout, QProgressBar, QCheckBox, QGroupBox, QSizePolicy, QFrame
)
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtCore import Qt


def build_page_3_ui():
    outer = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(16, 16, 16, 16)
    main_layout.setSpacing(4)

    # === config frame ===
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

    config_output = QTextEdit()
    config_output.setReadOnly(True)
    config_output.setStyleSheet("background-color: #fefefe; border: 1px solid #ddd;")
    config_output.setMinimumHeight(96)

    status_label = QLabel()
    status_label.setFont(QFont("Microsoft JhengHei", 10))
    status_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    config_layout.addLayout(title_layout)
    config_layout.addWidget(config_output)
    config_layout.addWidget(status_label)
    config_frame.setLayout(config_layout)
    main_layout.addWidget(config_frame)

    # === control area ===
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

    type_label = QLabel("選擇測試流程：")
    test_type_combo = QComboBox()
    test_type_combo.addItems(["type_1", "type_2", "type_3", "ALL"])

    debug_checkbox = QCheckBox("啟用 DEBUG 模式（封包紀錄）")

    type_layout.addWidget(type_label)
    type_layout.addWidget(test_type_combo)
    type_layout.addWidget(debug_checkbox)

    progress_bar = QProgressBar()
    progress_bar.setValue(0)
    progress_bar.setFormat("尚未開始")
    progress_bar.setFixedHeight(18)

    loading_gif = QLabel()
    movie = QMovie("workspace/assets/loading.gif")
    loading_gif.setMovie(movie)
    loading_gif.setVisible(False)

    control_layout.addLayout(type_layout)
    control_layout.addWidget(progress_bar)
    control_layout.addWidget(loading_gif)
    control_group.setLayout(control_layout)
    main_layout.addWidget(control_group)

    # === output area ===
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
    result_output.setLineWrapMode(QTextEdit.NoWrap)
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

    # === buttons ===
    btn_layout = QHBoxLayout()
    run_button = QPushButton("執行測試")
    back_button = QPushButton("返回上一頁")
    view_report_button = QPushButton("查看測試報表")
    view_report_button.setEnabled(False)
    export_log_button = QPushButton("匯出執行記錄")
    export_log_button.setEnabled(False)

    for btn in [run_button, back_button, view_report_button, export_log_button]:
        btn_layout.addWidget(btn)
    main_layout.addLayout(btn_layout)

    outer.setLayout(main_layout)

    return {
        "widget": outer,
        "copy_btn": copy_btn,
        "config_output": config_output,
        "status_label": status_label,
        "test_type_combo": test_type_combo,
        "debug_checkbox": debug_checkbox,
        "progress_bar": progress_bar,
        "loading_gif": loading_gif,
        "movie": movie,
        "result_output": result_output,
        "run_button": run_button,
        "back_button": back_button,
        "view_report_button": view_report_button,
        "export_log_button": export_log_button,
    }
