# workspace/controller/main_controller.py

"""
總控制器：依據 CLI 參數 --task 和 --type，執行登入與 WebSocket 任務流程
目前支援：001、009、001+009
"""

from workspace.controller.login.r88_login_controller import r88_login_flow
from workspace.controller.batch.ws_batch_controller_dev import run_ws_batch_dev
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode


def run_main_flow(task: str, game_type: str = "type_2") -> int:
    if task == "001":
        r88_login_flow("qa0002")
        return ResultCode.SUCCESS

    elif task == "009":
        run_ws_batch_dev(game_type)
        return ResultCode.SUCCESS

    elif task == "001+009":
        r88_login_flow("qa0002")
        task_list = run_ws_batch_dev(game_type)

        if task_list:
            print_info("✅ 第一筆完整任務資料：")
            print_info(str(task_list[0]))
            # 👉 此處可串接 ws_connection_flow(account=..., oid=...)

        return ResultCode.SUCCESS

    else:
        print_error(f"❌ 不支援的任務代號：{task}")
        return ResultCode.INVALID_TASK