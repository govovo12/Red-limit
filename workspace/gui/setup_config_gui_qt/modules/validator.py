from workspace.tools.validator.input_validator import validate_test_config


def validate_fields(pfid_input, key_input, rule_input,
                    pfid_err, key_err, rule_err, submit_btn):
    """
    檢查 GUI 中的欄位是否有效，更新錯誤提示與按鈕狀態。
    僅做為 GUI 橋接層，邏輯由工具模組處理。
    """
    pfid = pfid_input.text().strip()
    key = key_input.text().strip()
    rule = rule_input.text().strip()

    result = validate_test_config(pfid, key, rule)

    pfid_err.setText(result["pfid"]["message"])
    key_err.setText(result["private_key"]["message"])
    rule_err.setText(result["rule"]["message"])

    submit_btn.setEnabled(result["is_valid"])
