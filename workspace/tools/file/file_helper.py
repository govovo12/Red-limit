from pathlib import Path
from typing import Tuple
from workspace.tools.common.decorator import tool
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_error


@tool
def ensure_file(path: Path) -> Tuple[int, bool]:
    """
    確保檔案存在（若不存在則建立空檔），包含中間資料夾。

    :param path: 檔案路徑
    :return: (錯誤碼, 是否成功)
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.touch()
        return ResultCode.SUCCESS, True
    except Exception as e:
        print_error(f"建立檔案失敗：{e}")
        return ResultCode.TOOL_FILE_LOAD_FAILED, False


@tool
def is_file_empty(path: Path) -> Tuple[int, bool]:
    """
    檢查檔案是否為空（長度為 0）。

    :param path: 檔案路徑
    :return: (錯誤碼, 是否為空)
    """
    if not path.exists():
        return ResultCode.TOOL_FILE_NOT_FOUND, True
    if path.stat().st_size == 0:
        return ResultCode.TOOL_FILE_EMPTY, True
    return ResultCode.SUCCESS, False


@tool
def file_exists(path: Path) -> Tuple[int, bool]:
    """
    檢查檔案是否存在（僅檔案，不含資料夾）。

    :param path: 檢查的檔案路徑
    :return: (錯誤碼, 是否存在)
    """
    if path.exists() and path.is_file():
        return ResultCode.SUCCESS, True
    return ResultCode.TOOL_FILE_NOT_FOUND, False
