from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit, QVBoxLayout,
    QHBoxLayout, QProgressBar, QCheckBox, QGroupBox, QSizePolicy
)
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtCore import Qt
from workspace.config.paths import get_assets_dir


def build_page_3_ui():
    outer = QWidget()
    main_layout = QVBoxLayout(outer)
    main_layout.setContentsMargins(16, 16, 16, 16)
    main_layout.setSpacing(12)

    def create_card(title_text):
        card = QGroupBox("")
        card.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #f9f9f9;
                padding: 6px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel(title_text)
        title.setFont(QFont("Microsoft JhengHei", 11, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 6px;")
        layout.addWidget(title)

        return card, layout

    # === 測試環境設定區 ===
    config_group, config_layout = create_card("測試環境設定")
    config_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

    header_row = QHBoxLayout()
    copy_btn = QPushButton("📋")
    copy_btn.setToolTip("複製全部設定內容")
    copy_btn.setFixedSize(24, 24)
    copy_btn.setStyleSheet("font-size: 13px;")
    header_row.addStretch()
    header_row.addWidget(copy_btn)

    config_output = QTextEdit()
    config_output.setReadOnly(True)
    config_output.setMinimumHeight(60)
    config_output.setMaximumHeight(80)
    config_output.setStyleSheet("""
        QTextEdit {
            background-color: #ffffff;
            border: 1px solid #ddd;
            padding: 4px;
            font-size: 13px;
        }
    """)

    status_label = QLabel("✅ 設定已成功巾入")
    status_label.setStyleSheet("color: #2e7d32; font-size: 13px; margin-left: 6px;")
    status_label.setAlignment(Qt.AlignLeft)

    config_layout.addLayout(header_row)
    config_layout.addWidget(config_output)
    config_layout.addWidget(status_label)
    main_layout.addWidget(config_group)

    # === 控制區 ===
    control_group, control_layout = create_card("測試流程選擇與啟動")
    control_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    # 🟦 選擇區（上）
    form_row = QHBoxLayout()
    type_label = QLabel("選擇測試類型：")
    test_type_combo = QComboBox()
    test_type_combo.addItems(["type_1", "type_2", "type_3", "ALL"])
    test_type_combo.setCurrentText("ALL")
    debug_checkbox = QCheckBox("啟用 DEBUG 模式（封包紀錄）")
    form_row.addWidget(type_label)
    form_row.addWidget(test_type_combo)
    form_row.addStretch()
    form_row.addWidget(debug_checkbox)

    # 🟩 進度條 + 綿羊動畫 + 狀態文字
    progress_bar = QProgressBar()
    progress_bar.setValue(0)
    progress_bar.setFormat("")
    progress_bar.setFixedHeight(18)

    sheep_overlay = QWidget()
    sheep_overlay.setFixedHeight(40)
    sheep_overlay.setStyleSheet("background-color: transparent;")
    sheep_overlay.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    loading_gif = QLabel(sheep_overlay)
    loading_gif.resize(40, 40)
    loading_gif.move(0, 0)
    loading_gif.setVisible(False)
    movie = QMovie(str(get_assets_dir() / "loading.gif"))
    loading_gif.setMovie(movie)

    progress_status_label = QLabel("尚未開始")
    progress_status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    progress_status_label.setMinimumWidth(180)
    progress_status_label.setStyleSheet("color: #444; font-size: 13px; padding-left: 8px;")

    bar_and_label_row = QHBoxLayout()
    bar_and_label_row.addWidget(progress_bar, stretch=1)
    bar_and_label_row.addWidget(progress_status_label)

    progress_area = QVBoxLayout()
    progress_area.setSpacing(0)
    progress_area.setContentsMargins(0, 0, 0, 0)
    progress_area.addLayout(bar_and_label_row)
    progress_area.addWidget(sheep_overlay)

    # 🟨 底部按鈕區
    btn_layout = QHBoxLayout()
    run_button = QPushButton("執行測試")
    back_button = QPushButton("返回上一頁")
    view_report_button = QPushButton("查看測試報表")
    export_log_button = QPushButton("匯出執行記錄")

    view_report_button.setEnabled(False)
    export_log_button.setEnabled(False)

    for btn in [run_button, back_button, view_report_button, export_log_button]:
        btn.setMinimumWidth(120)
        btn_layout.addWidget(btn)

    control_layout.addLayout(form_row)
    control_layout.addLayout(progress_area)
    control_layout.addStretch()
    control_layout.addLayout(btn_layout)
    main_layout.addWidget(control_group)

    # === 執行輸出區 ===
    output_group, output_layout = create_card("執行輸出")
    result_output = QTextEdit()
    result_output.setReadOnly(True)
    result_output.setLineWrapMode(QTextEdit.NoWrap)  # ✅ 不折行，保留水平 scrollbar
    result_output.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # ✅ 需要時出現
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
    main_layout.addWidget(output_group)

    return {
        "widget": outer,
        "copy_btn": copy_btn,
        "config_output": config_output,
        "status_label": status_label,
        "test_type_combo": test_type_combo,
        "debug_checkbox": debug_checkbox,
        "progress_bar": progress_bar,
        "sheep_track": sheep_overlay,
        "loading_gif": loading_gif,
        "movie": movie,
        "result_output": result_output,
        "run_button": run_button,
        "back_button": back_button,
        "view_report_button": view_report_button,
        "export_log_button": export_log_button,
        "progress_status_label": progress_status_label,
    }
