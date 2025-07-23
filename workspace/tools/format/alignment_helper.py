import unicodedata

def pad_display_width(text: str, width: int) -> str:
    """
    根據 East Asian Width 對齊中英文混排字串顯示寬度。
    
    Args:
        text (str): 要對齊的文字。
        width (int): 顯示寬度（預期的字寬）。
    
    Returns:
        str: 補齊空白後的文字。
    """
    display_width = sum(2 if unicodedata.east_asian_width(ch) in 'WF' else 1 for ch in text)
    padding = width - display_width
    return text + ' ' * max(padding, 0)
