import json
from pathlib import Path
from typing import Any, Optional, Tuple
from workspace.tools.common.decorator import tool
from workspace.tools.printer.printer import print_error
from workspace.tools.common.result_code import ResultCode


@tool
def load_json(path: Path) -> Tuple[int, Optional[Any]]:
    """
    從指定檔案讀取 JSON 內容。

    :param path: JSON 檔案路徑
    :return: (錯誤碼, 資料物件)，若成功則錯誤碼為 SUCCESS
    """
    try:
        with path.open(encoding="utf-8") as f:
            return ResultCode.SUCCESS, json.load(f)
    except FileNotFoundError:
        print_error(f"找不到檔案：{path}")
        return ResultCode.TOOL_FILE_NOT_FOUND, None
    except json.JSONDecodeError:
        print_error(f"JSON 格式錯誤：{path}")
        return ResultCode.TOOL_FILE_JSON_INVALID, None
    except Exception as e:
        print_error(f"讀取 JSON 檔失敗：{e}")
        return ResultCode.TOOL_FILE_LOAD_FAILED, None


@tool
def save_json(data: Any, path: Path) -> Tuple[int, bool]:
    """
    將資料寫入指定 JSON 檔案。

    :param data: 要儲存的物件（dict 或 list）
    :param path: 要儲存的檔案路徑
    :return: (錯誤碼, 是否成功)
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return ResultCode.SUCCESS, True
    except Exception as e:
        print_error(f"寫入 JSON 檔失敗：{e}")
        return ResultCode.TOOL_FILE_LOAD_FAILED, False
