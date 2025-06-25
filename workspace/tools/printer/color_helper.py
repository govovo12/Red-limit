# ANSI 顏色輸出工具模組（可供 printer 或其他模組使用）
from workspace.tools.common.decorator import tool



@tool
def red(text: str) -> str:
    """將文字套用紅色樣式，用於錯誤訊息。"""
    return f"\033[91m{text}\033[0m"


@tool
def green(text: str) -> str:
    """將文字套用綠色樣式，用於成功訊息。"""
    return f"\033[92m{text}\033[0m"


@tool
def yellow(text: str) -> str:
    """將文字套用黃色樣式，用於警告訊息。"""
    return f"\033[93m{text}\033[0m"


@tool
def cyan(text: str) -> str:
    """將文字套用青色樣式，用於一般訊息。"""
    return f"\033[96m{text}\033[0m"
