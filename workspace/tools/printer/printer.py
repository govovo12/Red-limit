from datetime import datetime
from workspace.tools.printer.color_helper import yellow, green, red, cyan
from workspace.tools.common.decorator import tool




@tool

@tool
def print_info(msg: str, ctx=None, game_type=None) -> None:
    """
    輸出一般訊息，附帶時間戳記，使用 cyan 顏色。
    （不再進行 log 紀錄，log 將統一由總控處理）
    """
    print(f"{_timestamp()} {cyan('[INFO]')} {msg}")



@tool
def print_success(msg: str) -> None:
    """
    輸出成功訊息，附帶時間戳記，使用 green 顏色。
    """
    print(f"{_timestamp()} {green('[SUCCESS]')} {msg}")


@tool
def print_warning(msg: str) -> None:
    """
    輸出警告訊息，附帶時間戳記，使用 yellow 顏色。
    """
    print(f"{_timestamp()} {yellow('[WARNING]')} {msg}")


@tool
def print_error(msg: str) -> None:
    """
    輸出錯誤訊息，附帶時間戳記，使用 red 顏色。
    """
    print(f"{_timestamp()} {red('[ERROR]')} {msg}")

@tool
def _timestamp() -> str:
    """
    取得目前時間戳記字串（格式：YYYY-MM-DD HH:MM:SS）
    """
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
