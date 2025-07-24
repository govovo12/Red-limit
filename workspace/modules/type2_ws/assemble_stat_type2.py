# ================================================================
# 🧮 assemble_stat_type2.py | Step 8 組合限紅統計報表（type_2 專用）
# ================================================================

# 📌 任務錯誤碼（只 import ResultCode 即可）
from workspace.tools.common.result_code import ResultCode

# ⚙️ DEBUG 開關
from workspace.tools.env.config_loader import DEBUG_WS_PACKET


def assemble_stat(data: dict) -> tuple[dict, int]:
    if DEBUG_WS_PACKET:
        print("[DEBUG] assemble_stat_type2 input =", data)

    try:
        actual = int(data["actual"])
        rule = data.get("expect", "UNKNOWN")  # ✅ 改名，避免混淆
        code = int(data["code"])
    except Exception:
        return {}, ResultCode.TASK_TYPE2_STAT_ASSEMBLY_FAILED

    passed = code == ResultCode.SUCCESS
    stat = {
        "Game": data["game"],
        "Account": data["account"],
        "Expect": rule,               # ✅ 直接顯示原本就是 >=10 的字串
        "Actual": actual,
        "Mark": "✅ Passed" if passed else "❌ Failed"
    }

    return stat, ResultCode.SUCCESS
