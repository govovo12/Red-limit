# workspace/controller/main_controller.py

"""
總控制器：依據 CLI 參數 --task 和 --type，執行登入與 WebSocket 任務流程
目前支援：001、009、001+009
"""

from workspace.controller.login.r88_login_controller import r88_login_flow
from workspace.controller.batch.ws_batch_controller_dev import run_ws_batch_dev
from workspace.tools.router.task_dispatcher import get_handler_by_type
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode
import json
from concurrent.futures import ThreadPoolExecutor

def run_main_flow(task: str, game_type: str = "type_2") -> int:
    if task == "001":
        r88_login_flow("qa0002")
        return ResultCode.SUCCESS

    elif task == "009":
        run_ws_batch_dev(game_type)
        return ResultCode.SUCCESS

    elif task == "001+009":
        r88_login_flow("qa0002")

        # ✅ 執行任務 009：取得所有 type 的任務包
        task_dict = run_ws_batch_dev(game_type)
        print_info("🧩 總控接收到的完整任務 dict 結構如下：")
        print(json.dumps(task_dict, indent=2, ensure_ascii=False))

        # ✅ 依照 type 分派子控
        for type_key, bundle in task_dict.items():
            print_info(f"✅ 第一筆 {type_key} 任務資料：")
            first_task = bundle["data"][type_key][0]
            print_info(json.dumps(first_task, indent=2, ensure_ascii=False))

            task_list = bundle["data"][type_key]
            count = bundle["count"]

            handler = get_handler_by_type(type_key)

            if handler:
                print_info(f"🚀 啟動 {type_key} 子控，並行數：{count}")
                with ThreadPoolExecutor(max_workers=count) as executor:
                    futures = [
                        executor.submit(handler, task)  # ✅ 傳送 task
                        for task in task_list
                    ]
                    for i, future in enumerate(futures):
                        try:
                            code = future.result(timeout=10)  # 最多等 10 秒，避免卡死
                        except Exception as e:
                            failed_task = task_list[i]
                            oid = failed_task.get("oid", "?")
                            game = failed_task.get("game_name", "?")
                            print_error(f"❌ 子控執行失敗：oid={oid}, game={game}, error={e}")

            else:
                print_error(f"❌ 不支援的任務類型：{type_key}")
                return ResultCode.INVALID_TASK

        return ResultCode.SUCCESS

    else:
        print_error(f"❌ 不支援的任務代號：{task}")
        return ResultCode.INVALID_TASK
