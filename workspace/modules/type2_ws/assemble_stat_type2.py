# ================================================================
# 🧮 assemble_stat_type2.py | Step 8 組合限紅統計報表（type_2 專用）
# ================================================================

# 📌 任務錯誤碼（只 import ResultCode 即可）
from workspace.tools.common.result_code import ResultCode

# ⚙️ DEBUG 開關
from workspace.tools.env.config_loader import DEBUG_WS_PACKET


def assemble_stat(data: dict) -> tuple[dict, int]:
    """
    組合統計報表用的 stat 字典（type_2 限紅驗證用）。

    Args:
        data (dict): 子控制器提供的統計資料，格式為：
            {
                "game": 遊戲名稱,
                "account": 帳號名稱,
                "expect": 預期下注金額（int 或 str 型態）,
                "actual": 實際下注金額（int 或 str 型態）,
                "code": 限紅驗證結果碼（來自 step_7）
            }

    Returns:
        Tuple[dict, int]: 
            - stat: 組裝完成的統計字典（含 Game, Account, Expect, Actual, Mark）
            - ResultCode.SUCCESS：固定為成功，因為這只是報表
    """
    if DEBUG_WS_PACKET:
        print("[DEBUG] assemble_stat_type2 input =", data)

    try:
        actual = int(data["actual"])
        expect = int(data["expect"])
        code = int(data["code"])
    except Exception:
        return {}, ResultCode.TASK_TYPE2_STAT_ASSEMBLY_FAILED

    passed = code == ResultCode.SUCCESS
    stat = {
        "Game": data["game"],
        "Account": data["account"],
        "Expect": f">={expect}",
        "Actual": actual,
        "Mark": "✅ Passed" if passed else "❌ Failed"
    }

    return stat, ResultCode.SUCCESS
