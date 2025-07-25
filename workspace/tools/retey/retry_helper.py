"""
retry_helper.py

提供 retry_with_log 函式，支援：
- 任務模組失敗回傳錯誤碼時，自動呼叫 log_step_result 印出錯誤訊息
- 持續要求直到回傳成功結果（dict 型）
"""

from workspace.tools.common.log_helper import log_step_result
from workspace.tools.common.result_code import ResultCode
from typing import Callable, Union, Dict


def retry_with_log(task_func: Callable[[], Union[int, Dict]], step: str = "未知步驟") -> Dict:
    """
    不斷執行 task_func，直到其回傳成功（dict）為止。
    若回傳錯誤碼，會自動印出錯誤訊息並重新執行。
    """
    while True:
        result = task_func()
        if isinstance(result, dict):
            return result
        if isinstance(result, int):
            log_step_result(result, step)
        else:
            log_step_result(ResultCode.TASK_EXCEPTION, step)

