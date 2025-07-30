# ✅ Type 3 統計格式轉換任務模組（支援 code 傳入）

from workspace.tools.common.result_code import ResultCode

async def assemble_stat(
    account: str,
    game_name: str,
    expected: str = None,
    actual: float = None,
    code: int = ResultCode.SUCCESS,
    debug: bool = False
) -> tuple[dict, int]:
    """
    將 Type 3 的限紅資料轉換為標準統計格式，支援外部傳入錯誤碼，與 type 1/2 統一。
    """

    try:
        if code != ResultCode.SUCCESS:
            # 由子控傳入失敗碼 → 不執行比對
            stat = {
                "Game": game_name,
                "Account": account,
                "Expect": expected,
                "Actual": actual,
                "Mark": "❌ Failed"
            }
            return stat, code

        # ✅ 成功時執行比對
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
            print(f"[DEBUG] 統計 expect={expected} actual={actual} result={mark} stat={stat}")

        return stat, ResultCode.SUCCESS

    except Exception:
        return {}, ResultCode.TASK_TYPE3_STAT_ASSEMBLY_FAILED
