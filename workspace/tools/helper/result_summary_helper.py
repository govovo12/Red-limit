# workspace/tools/helper/result_summary_helper.py

from typing import Dict, List
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode


def summarize_task_result(task_type: str, result: Dict[str, List[Dict]]) -> int:
    """
    工具：統計單一子控的執行結果，並輸出 summary 訊息

    Args:
        task_type (str): 任務類型（例如 type_2）
        result (dict): 子控回傳的任務結果包 {"success": [...], "fail": [...]}

    Returns:
        int: 若有失敗回傳 TASK_SUBCONTROLLER_FAILED，否則 SUCCESS
    """
    success_count = len(result.get("success", []))
    fail_list = result.get("fail", [])

    print_info(f"📊 {task_type} 執行結果：成功 {success_count} 條，失敗 {len(fail_list)} 條")

    if fail_list:
        print_error(f"❌ {task_type} 有失敗任務（僅列出 oid + game_name + error_code）：")
        for task in fail_list:
            print_error(f"- oid={task.get('oid')} game={task.get('game_name')} error_code={task.get('error_code')}")
        return ResultCode.TASK_SUBCONTROLLER_FAILED

    return ResultCode.SUCCESS
