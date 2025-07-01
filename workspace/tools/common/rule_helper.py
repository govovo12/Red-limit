"""
通用規則解析工具，例如從金額規則中提取數值
"""

import re

def extract_number_from_rule(rule: str) -> float:
    """
    從字串中抓出第一個數值（無論符號），純粹取出金額用

    Args:
        rule (str): 例如 ">=0.1", "<=100", "=999", ">0.01"

    Returns:
        float: 提取的數值，例如 0.1
    """
    match = re.search(r"\d+(\.\d+)?", rule)
    if match:
        return float(match.group(0))
    raise ValueError(f"無法從規則中解析出數值: {rule}")
