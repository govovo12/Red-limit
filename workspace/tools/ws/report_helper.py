# report_helper.py

from workspace.tools.printer.printer import print_info
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.common.result_code import ResultCode


def report_step_result(ctx, code: int, step: str, error_records: list):
    """
    統一處理任務步驟回報：
    - 印出錯誤 log（僅一次）
    - 錯誤碼記錄給總控（ctx.code）
    - 錯誤碼記錄給子控 log（ctx.all_codes, step_code_map）
    - 支援容忍錯誤不中斷流程
    """

    # ✅ 印出錯誤/成功 log
    log_step_result(code, step=step, account=ctx.account, game_name=ctx.game_name)

    # ✅ 記錄錯誤碼（供後續統計）
    if code != ResultCode.SUCCESS:
        if code not in ctx.all_codes:
            ctx.all_codes.append(code)
        ctx.step_code_map[step] = code

    # ✅ 回傳主控錯誤碼（只記第一個錯）
    if ctx.code == ResultCode.SUCCESS and code != ResultCode.SUCCESS:
        ctx.code = code

    # ✅ 這些錯誤會被記錄，但不中斷流程
    tolerated = {
        ResultCode.TASK_BET_MISMATCHED,
        ResultCode.TASK_BET_AMOUNT_VIOLATED,
    }

    if code in tolerated:
        print_info(f"[Warning] ⚠ 容忍錯誤 code={code} at step={step}")
        error_records.append({
            "code": code,
            "step": step,
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
        return

    # ✅ 非容忍錯誤 → 中斷
    if code != ResultCode.SUCCESS:
        ctx.ok = False
        error_records.append({
            "code": code,
            "step": step,
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
