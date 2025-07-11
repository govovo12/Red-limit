from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.printer.printer import print_info

def report_step_result(ctx, code: int, step: str, error_records: list):
    """
    子控制器專用：統一處理錯誤碼、容忍錯誤、流程中斷與錯誤記錄。
    """
    log_step_result(code, step=step, account=ctx.account, game_name=ctx.game_name)

    if code == ResultCode.SUCCESS:
        return

    # 可容忍錯誤碼區（可自訂擴充）
    tolerated = {
        ResultCode.TASK_BET_MISMATCHED,
        ResultCode.TASK_BET_AMOUNT_VIOLATED,
    }

    if code in tolerated:
        print_info(f"[Warning] ⚠ 容忍錯誤 code={code} at step={step}")
        ctx.code = code  # ✅ 有記錄錯誤碼，但不中斷流程
        error_records.append({
            "code": code,
            "step": step,
            "account": ctx.account,
            "game_name": ctx.game_name,
        })
        return

    # ⛔ 一般錯誤 → 中斷流程
    ctx.ok = False
    ctx.code = code
    error_records.append({
        "code": code,
        "step": step,
        "account": ctx.account,
        "game_name": ctx.game_name,
    })
