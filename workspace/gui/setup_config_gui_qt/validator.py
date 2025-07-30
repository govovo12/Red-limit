from workspace.config.setup_config.input_validator import (
    validate_pf_id, validate_private_key
)
from workspace.tools.common.result_code import ResultCode
from dotenv import dotenv_values
from pathlib import Path

def validate_fields(pfid_input, key_input, rule_input,
                    pfid_err, key_err, rule_err, submit_btn):
    """
    檢查 GUI 中的欄位是否有效，並更新錯誤提示與送出按鈕狀態。
    專用於初始化頁面的驗證流程。
    """
    pfid = pfid_input.text().strip()
    key = key_input.text().strip()
    rule_val = rule_input.text().strip()
    valid = True

    _, code = validate_pf_id(pfid)
    pfid_err.setText("" if code == ResultCode.SUCCESS else "格式錯誤：需含底線，僅限英數字")
    valid &= code == ResultCode.SUCCESS

    _, code = validate_private_key(key)
    key_err.setText("" if code == ResultCode.SUCCESS else "金鑰錯誤：32 碼英數字")
    valid &= code == ResultCode.SUCCESS

    try:
        float(rule_val)
        rule_err.setText("")
    except ValueError:
        rule_err.setText("請輸入有效數值")
        valid = False

    submit_btn.setEnabled(valid)

def load_user_config():
    """
    載入 .env.user 的所有 key-value 組。
    回傳 dict，例如：
    {
        "PF_ID": "qa0002",
        "PRIVATE_KEY": "...",
        ...
    }
    """
    env_path = Path(__file__).resolve().parents[3] / ".env.user"
    return dotenv_values(env_path)