from workspace.gui.setup_config_gui_qt.page_2.page_2_ui import build_page_2_ui
from workspace.gui.setup_config_gui_qt.page_2.page_2_ux import handle_submit
from workspace.gui.setup_config_gui_qt.modules.validator import validate_fields


def register_page2(stack_widget, go_to_page3):
    ui = build_page_2_ui()
    bind_input_validation(ui)

    # ✅ 送出 → 呼叫 handle_submit
    ui["submit_btn"].clicked.connect(lambda: handle_submit(ui, stack_widget, go_to_page3))

    # ✅ 返回 Page1（index 0）
    ui["return_btn"].clicked.connect(lambda: stack_widget.setCurrentIndex(0))

    # ✅ 跳過設定 → 直接進 Page3（刷新）
    ui["skip_btn"].clicked.connect(lambda: go_to_page3())

    stack_widget.addWidget(ui["page"])


def bind_input_validation(ui):
    """
    綁定輸入欄位與驗證邏輯，控制錯誤顯示與送出按鈕啟用。
    """
    pfid_input = ui["pfid_input"]
    key_input = ui["key_input"]
    rule_input = ui["rule_input"]
    rule_combo = ui["rule_combo"]
    pfid_err = ui["pfid_err"]
    key_err = ui["key_err"]
    rule_err = ui["rule_err"]
    submit_btn = ui["submit_btn"]
    key_length_label = ui["key_length_label"]  # ✅ 額外新增

    def update_key_length():
        key_length_label.setText(f"{len(key_input.text().strip())} / 32")

    validate = lambda: validate_fields(
        pfid_input, key_input, rule_input,
        pfid_err, key_err, rule_err,
        submit_btn
    )

    pfid_input.textChanged.connect(validate)
    key_input.textChanged.connect(validate)
    rule_input.textChanged.connect(validate)
    rule_combo.currentTextChanged.connect(validate)

    # ✅ 加上即時更新 PRIVATE_KEY 長度顯示
    key_input.textChanged.connect(update_key_length)
