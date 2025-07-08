

import logging
from typing import Optional

from workspace.tools.common.result_code import ResultCode

SUCCESS_CODES = ResultCode.SUCCESS_CODES
TOOL_ERROR_CODES = ResultCode.TOOL_ERROR_CODES
TASK_ERROR_CODES = ResultCode.TASK_ERROR_CODES
ERROR_MESSAGES = ResultCode.ERROR_MESSAGES

logger = logging.getLogger(__name__)


def log_simple_result(code: int, context: Optional[str] = None) -> None:
    """
    根據錯誤碼輸出對應狀態與訊息，寫入 CLI 與 logger。

    Args:
        code (int): 錯誤碼
        context (Optional[str]): 額外描述內容（例如 step/account/game）
    """
    msg = ERROR_MESSAGES.get(code, "未知錯誤")

    if code in SUCCESS_CODES:
        status = "✅ 成功"
    elif code in TOOL_ERROR_CODES:
        status = "❌ 工具錯誤"
    elif code in TASK_ERROR_CODES:
        status = "▲ 任務錯誤"
    else:
        status = "❓ 未知錯誤"

    full_msg = f"[{status}] code={code} msg={msg}"
    if context:
        full_msg += f" - {context}"

    print(full_msg)
    logger.info(full_msg)


def log_step_result(
    code: int,
    step: str,
    account: Optional[str] = None,
    game_name: Optional[str] = None,
    extra: Optional[str] = None,
) -> None:
    """
    子控流程專用錯誤碼輸出格式（加上帳號、遊戲、步驟等欄位）

    Args:
        code (int): 錯誤碼
        step (str): 所在流程步驟
        account (str): 登入帳號
        game_name (str): 遊戲名稱
        extra (str): 額外補充資訊
    """
    context = f"step={step}"
    if account:
        context += f" | account={account}"
    if game_name:
        context += f" | game={game_name}"
    if extra:
        context += f" | {extra}"

    log_simple_result(code, context)
