from typing import Optional
from workspace.tools.common.result_code import (
    ResultCode,
    SUCCESS_CODES,
    TOOL_ERROR_CODES,
    TASK_ERROR_CODES,
    GENERIC_ERROR_CODES,
    ERROR_MESSAGES,  # ← ✅ 正確名稱
)

from workspace.tools.printer.printer import print_info, print_error


def log_simple_result(
    code: int,
    context: Optional[str] = None,
    oid: Optional[str] = None
) -> None:
    """
    根據錯誤碼分類與訊息輸出格式化資訊

    - 成功碼使用 print_info
    - 其他錯誤使用 print_error
    - 支援錯誤分類（工具錯誤 / 任務錯誤 / 通用錯誤）
    - 可附加 OID 為 context 訊息
    """
    msg = ERROR_MESSAGES.get(code, "未知錯誤")

    if code in SUCCESS_CODES:
        label = "✅ 成功"
        printer = print_info
    elif code in TOOL_ERROR_CODES:
        label = "❌ 工具錯誤"
        printer = print_error
    elif code in TASK_ERROR_CODES:
        label = "📦 任務錯誤"
        printer = print_error
    elif code in GENERIC_ERROR_CODES:
        label = "❓ 通用錯誤"
        printer = print_error
    else:
        label = "❓ 未知類型"
        printer = print_error

    # 🔧 組合錯誤訊息
    full_msg = f"[{label}] code={code} msg={msg}"
    if context:
        full_msg += f" - {context}"
    if oid:
        full_msg += f" / oid={oid}"

    printer(full_msg)
