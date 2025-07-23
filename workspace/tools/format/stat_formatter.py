# ================================================================
# 📄 stat_formatter.py | 格式化統計資料報表（限紅結果等）對齊輸出工具
# ================================================================

# 🔢 工具模組錯誤碼區（40010～）
# ------------------------------------------------
from workspace.tools.common.result_code import ResultCode

# 🔧 工具模組
# ------------------------------------------------
from workspace.tools.format.alignment_helper import pad_display_width
# 🔎 模組內使用的編碼工具
import unicodedata

def format_stat_lines(stat_list: list[dict]) -> list[str]:
    """
    將統計資料 dict 陣列格式化為對齊的報表列字串。

    Args:
        stat_list (list[dict]): 每筆為統一格式的報表資料，
            範例如下：
            {
                "Game": "福星聚宝",
                "Account": "qa0006",
                "Expect": ">=10",
                "Actual": 10,
                "Mark": "✅ Passed"
            }

    Returns:
        list[str]: 每行為對齊後的字串，如：
            [
                "Game : 福星聚宝 | Account : qa0006 | Expect : >=10 | Actual : 10 | ✅ Passed",
                "Game : 钱滚钱   | Account : qa0071 | Expect : >=10 | Actual :  1 | ❌ Failed"
            ]
    """
    if not isinstance(stat_list, list) or not all(isinstance(d, dict) for d in stat_list):
        raise ValueError(ResultCode.TOOL_STAT_FORMAT_INVALID_INPUT)

    fields = ["Game", "Account", "Expect", "Actual"]
    max_width = {key: len(key) for key in fields}

    # 計算欄位最大寬度（含中英文混排）
    for entry in stat_list:
        for key in fields:
            val = str(entry.get(key, ""))
            width = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in val)
            max_width[key] = max(max_width[key], width)

    # 組合每一行
    lines = []
    for entry in stat_list:
        parts = []
        for key in fields:
            val = str(entry.get(key, ""))
            padded = pad_display_width(val, max_width[key])
            parts.append(f"{key} : {padded}")
        parts.append(entry.get("Mark", ""))
        lines.append(" | ".join(parts))

    return lines



