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

def run_main_flow(task: str, game_type: str = "type_2") -> int:
    if task == "001":
        r88_login_flow("qa0002")
        return ResultCode.SUCCESS

    elif task == "009":
        run_ws_batch_dev(game_type)
        return ResultCode.SUCCESS

    elif task == "001+009":
        # ✅ Step 1: 登入帳號
        r88_login_flow("qa0002")

        # ✅ Step 2: 執行任務 009，取得所有 type 的任務包
        task_dict = run_ws_batch_dev(game_type)
        print_info("🧩 總控接收到的完整任務 dict 結構如下：")
        print(json.dumps(task_dict, indent=2, ensure_ascii=False))

        # ✅ Step 3: 依據 type 分派對應的子控
        for type_key, bundle in task_dict.items():
            task_list = bundle["data"][type_key]  # 取全部任務
            count = len(task_list)  # 根據任務數量決定併發
            handler = get_handler_by_type(type_key)

            if handler:
                print_info(f"✅ 第一筆 {type_key} 任務資料：")
                print(json.dumps(task_list[0], indent=2, ensure_ascii=False))

                print_info(f"🚀 啟動 {type_key} 子控，最大併發數：{count}")
                result = handler(task_list=task_list, max_concurrency=count)

                print_info(f"📦 {type_key} 子控執行完成，錯誤碼列表如下：")
                print(result)

                if any(code != ResultCode.SUCCESS for code in result):
                    print_error(f"❌ {type_key} 子控有錯誤發生")
                    return ResultCode.TASK_PARTIAL_FAILED

            else:
                print_error(f"❌ 不支援的任務類型：{type_key}")
                return ResultCode.INVALID_TASK

    return ResultCode.SUCCESS