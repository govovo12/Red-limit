from typing import Any, Optional, Tuple
from workspace.tools.common.decorator import tool
from workspace.tools.printer.printer import print_error
from workspace.tools.common.result_code import ResultCode


@tool
def assert_status_code(actual: int, expected: int = 200) -> Tuple[int, bool]:
    """
    檢查 HTTP status code 是否符合預期。

    :return: (錯誤碼, 是否通過)
    """
    if actual != expected:
        print_error(f"Status code 錯誤：預期 {expected}, 實際 {actual}")
        return ResultCode.TOOL_ASSERT_STATUS_CODE_FAIL, False
    return ResultCode.SUCCESS, True


@tool
def assert_keys_exist(data: dict, required_keys: list[str]) -> Tuple[int, bool]:
    """
    確保指定的 key 都存在於資料 dict 中。

    :return: (錯誤碼, 是否通過)
    """
    missing = [k for k in required_keys if k not in data]
    if missing:
        print_error(f"缺少欄位：{missing}")
        return ResultCode.TOOL_ASSERT_KEY_MISSING, False
    return ResultCode.SUCCESS, True


@tool
def assert_data_is_list(data: Any) -> Tuple[int, bool]:
    """
    檢查資料是否為 list 格式。

    :return: (錯誤碼, 是否通過)
    """
    if not isinstance(data, list):
        print_error("回傳資料不是 list")
        return ResultCode.TOOL_ASSERT_DATA_NOT_LIST, False
    return ResultCode.SUCCESS, True


@tool
def assert_list_not_empty(data: list) -> Tuple[int, bool]:
    """
    檢查 list 是否為空。

    :return: (錯誤碼, 是否通過)
    """
    if len(data) == 0:
        print_error("list 為空，無資料可處理")
        return ResultCode.TOOL_ASSERT_LIST_EMPTY, False
    return ResultCode.SUCCESS, True

@tool
def assert_values_equal(actual: Any, expected: Any, label: str = "") -> Tuple[int, bool]:
    """
    檢查兩個值是否相等。
    回傳 (錯誤碼, 驗證結果)，不相等時會印出錯誤訊息。

    :param actual: 實際值
    :param expected: 預期值
    :param label: 錯誤訊息標籤
    :return: (錯誤碼, 是否通過)
    """
    if actual != expected:
        print_error(f"{label} 不一致：預期 {expected}，實際 {actual}")
        return ResultCode.TOOL_ASSERT_VALUE_MISMATCH, False
    return ResultCode.SUCCESS, True