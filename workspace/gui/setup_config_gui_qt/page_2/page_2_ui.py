from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QComboBox, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt
from workspace.gui.setup_config_gui_qt.validator import validate_fields


def create_label(text):
    return QLabel(text)


def create_error_label():
    label = QLabel("")  # ✅ 預設空文字，不隱藏，保持 layout 穩定
    label.setStyleSheet("color: red")
    return label


def create_combo(items):
    combo = QComboBox()
    combo.addItems(items)
    return combo


def create_page2_ui(stack_widget):
    page = QWidget()
    outer_layout = QVBoxLayout(page)

    # 上：設定區塊（最多撐高一點，避免把說明擠飛）
    setting_section = QFrame()
    setting_section.setMaximumHeight(420)
    setting_layout = QVBoxLayout(setting_section)
    setting_layout.addWidget(QLabel("🎮 參數設定頁", alignment=Qt.AlignCenter))

    # PF_ID
    pfid_label = create_label("PF_ID")
    pfid_input = QLineEdit()
    pfid_input.setPlaceholderText("請輸入 PF_ID")
    pfid_err = create_error_label()

    # PRIVATE_KEY
    key_label = create_label("PRIVATE_KEY")
    key_input = QLineEdit()
    key_input.setPlaceholderText("請輸入 32 碼金鑰")
    key_input.setEchoMode(QLineEdit.Password)
    key_err = create_error_label()

    # 限紅邏輯
    mode_label = create_label("限紅邏輯模式")
    mode_combo = create_combo(["最大限紅", "最小限紅"])
    mode_err = create_error_label()  # ✅ 保持欄位一致高度

    # 限紅規則
    rule_label = create_label("限紅規則運算")
    rule_combo = create_combo([">=", "<=", "==", ">", "<"])
    rule_input = QLineEdit()
    rule_input.setPlaceholderText("數值")
    rule_err = create_error_label()

    rule_layout = QHBoxLayout()
    rule_layout.addWidget(rule_combo)
    rule_layout.addWidget(rule_input)

    # 按鈕區
    submit_btn = QPushButton("送出設定 ✅")
    submit_btn.setEnabled(False)
    skip_btn = QPushButton("跳過設定 ➤")
    btns = QHBoxLayout()
    btns.addWidget(submit_btn)
    btns.addWidget(skip_btn)

    # 加入所有元件到設定 layout
    setting_layout.addWidget(pfid_label)
    setting_layout.addWidget(pfid_input)
    setting_layout.addWidget(pfid_err)

    setting_layout.addWidget(key_label)
    setting_layout.addWidget(key_input)
    setting_layout.addWidget(key_err)

    setting_layout.addWidget(mode_label)
    setting_layout.addWidget(mode_combo)
    setting_layout.addWidget(mode_err)

    setting_layout.addWidget(rule_label)
    setting_layout.addLayout(rule_layout)
    setting_layout.addWidget(rule_err)

    setting_layout.addLayout(btns)

    # 下：說明或其他保留區（目前先空白）
    desc_section = QFrame()
    desc_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # 外部排版
    outer_layout.addWidget(setting_section)
    outer_layout.addWidget(desc_section)

    widgets = {
        "page": page,
        "pfid_input": pfid_input,
        "key_input": key_input,
        "mode_combo": mode_combo,
        "rule_combo": rule_combo,
        "rule_input": rule_input,
        "pfid_err": pfid_err,
        "key_err": key_err,
        "rule_err": rule_err,
        "submit_btn": submit_btn,
        "skip_btn": skip_btn,
    }

    return widgets
