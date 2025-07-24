# ✅ Type 3 統計格式轉換任務模組

from workspace.tools.common.result_code import ResultCode

async def assemble_stat(account: str, game_name: str, expected: str, actual: float, debug: bool = False) -> tuple[dict, int]:
    """
    將 Type 3 的限紅資料轉換為標準統計格式，回傳給子控用於後續排版。
    """
    try:
        passed = eval(f"{actual} {expected.replace('>=', '>=')}")
        mark = "✅ Passed" if passed else "❌ Failed"

        stat = {
            "Game": game_name,
            "Account": account,
            "Expect": expected,
            "Actual": actual,
            "Mark": mark
        }

        if debug:
            print(f"[DEBUG] Step 7 統計：expect={expected} actual={actual} stat={stat}")

        return stat, ResultCode.SUCCESS  # ✅ 修正回傳順序

    except Exception:
        return {}, ResultCode.TASK_TYPE3_STAT_ASSEMBLY_FAILED  # ✅ 錯誤順序也修正
