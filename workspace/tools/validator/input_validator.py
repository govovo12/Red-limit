from workspace.tools.common.result_code import ResultCode
import re


def validate_pf_id(pfid: str):
    """
    驗證 PF_ID：需含底線，僅限英文與數字
    - 必須符合正規表達式：只含英文、數字、底線
    - 必須包含至少一個底線 _
    """
    if "_" not in pfid:
        return pfid, ResultCode.TASK_INVALID_PFID
    if re.fullmatch(r"[A-Za-z0-9_]+", pfid):
        return pfid, ResultCode.SUCCESS
    return pfid, ResultCode.TASK_INVALID_PFID



def validate_private_key(key: str):
    """驗證 PRIVATE_KEY：允許任意 32 碼英文與數字（非十六進位）"""
    if re.fullmatch(r"[A-Za-z0-9]{32}", key):
        return key, ResultCode.SUCCESS
    return key, ResultCode.TASK_INVALID_PRIVATE_KEY


def validate_test_config(pfid: str, private_key: str, rule: str) -> dict:
    """
    驗證測試設定輸入欄位，回傳每個欄位的錯誤碼與錯誤訊息。
    適合提供給 GUI、CLI 或其他層使用，不依賴任何介面物件。
    """
    result = {}

    # ✅ PF_ID 驗證
    _, pfid_code = validate_pf_id(pfid.strip())
    result["pfid"] = {
        "code": pfid_code,
        "message": "" if pfid_code == ResultCode.SUCCESS else "格式錯誤：需含底線，僅限英數字"
    }

    # ✅ PRIVATE_KEY 驗證
    _, key_code = validate_private_key(private_key.strip())
    result["private_key"] = {
        "code": key_code,
        "message": "" if key_code == ResultCode.SUCCESS else "金鑰錯誤：32 碼英數字"
    }

    # ✅ 金額數字驗證
    try:
        float(rule.strip())
        rule_code = ResultCode.SUCCESS
        rule_msg = ""
    except ValueError:
        rule_code = ResultCode.TOOL_INVALID_RULE_VALUE
        rule_msg = "請輸入有效數值"

    result["rule"] = {
        "code": rule_code,
        "message": rule_msg
    }

    # ✅ 總驗證結果
    result["is_valid"] = all(v["code"] == ResultCode.SUCCESS for v in result.values() if isinstance(v, dict))
    return result
