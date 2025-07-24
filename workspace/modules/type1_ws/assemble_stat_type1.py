"""
組裝 Type 1 遊戲的限紅驗證結果為報表格式，供子控制器後續排版與統整使用。
此模組不做排版與 log，僅格式轉換。
"""

from workspace.tools.common.result_code import ResultCode


def assemble_stat(data: dict) -> tuple[dict, int]:
    """
    將驗證結果轉換為固定格式的報表資料。

    Args:
        data (dict): 包含以下欄位：
            - account (str)
            - game (str)
            - expect (Any)
            - actual (Any)
            - code (int)

    Returns:
        tuple: (stat dict, error code)
    """
    try:
        stat = {
            "Game": data.get("game", ""),
            "Account": data.get("account", ""),
            "Expect": str(data.get("expect")),
            "Actual": data.get("actual"),
            "Mark": "✅ Passed" if data.get("code") == ResultCode.SUCCESS else "❌ Failed",
        }
        return stat, ResultCode.SUCCESS
    except Exception:
        return {}, ResultCode.TASK_TYPE1_STAT_ASSEMBLY_FAILED
