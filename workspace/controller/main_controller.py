from workspace.controller.login.r88_login_controller import r88_login_flow
from workspace.controller.batch.ws_batch_controller_dev import run_ws_batch_dev
from workspace.tools.router.task_dispatcher import get_handler_by_type
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.common.result_code import ResultCode
from workspace.tools.env.config_loader import TASK_LIST_MODE, CONCURRENCY_MODE
import json


def run_main_flow(task: str, game_type: str = None) -> int:
    if task == "001":
        r88_login_flow("qa0002")
        return ResultCode.SUCCESS

    elif task == "009":
        if not game_type:
            print_error("❌ 請指定 --type（例如 type_2 或 ALL）")
            return ResultCode.INVALID_TASK

        task_dict = run_ws_batch_dev(game_type)
        print_info("🧩 任務 009 結果如下：")
        print(json.dumps(task_dict, indent=2, ensure_ascii=False))
        return ResultCode.SUCCESS

    elif task == "001+009":
        # ✅ Step 1: 執行登入
        r88_login_flow("qa0002")

        # ✅ Step 2: 若未指定 type，僅執行登入與 access_token，不進入任何 ws 子控流程
        if not game_type:
            print_info("ℹ️ 未指定 --type，僅執行登入與 access_token，未執行任何子控流程")
            return ResultCode.SUCCESS

        # ✅ Step 3: 開始處理指定 type（ALL 或單一）
        task_dict = run_ws_batch_dev(game_type)
        print_info("🧩 總控接收到的完整任務 dict 結構如下：")
        print(json.dumps(task_dict, indent=2, ensure_ascii=False))

        if game_type == "ALL":
            print_info("ℹ️ 已列出所有類型任務資料，未執行任何子控流程")
            return ResultCode.SUCCESS

        # ✅ Step 4: 執行子控
        for type_key, bundle in task_dict.items():
            data_list = bundle["data"][type_key]

            print_info(f"[ENV] 使用 task_list={TASK_LIST_MODE}, count={CONCURRENCY_MODE}")

            if TASK_LIST_MODE == "all":
                task_list = data_list
            elif TASK_LIST_MODE.isdigit() and int(TASK_LIST_MODE) < len(data_list):
                task_list = [data_list[int(TASK_LIST_MODE)]]
            else:
                print_error(f"❌ 無效的 task_list 設定：{TASK_LIST_MODE}")
                return ResultCode.INVALID_TASK

            if CONCURRENCY_MODE == "all":
                count = bundle.get("count", len(task_list))
            elif CONCURRENCY_MODE.isdigit():
                count = int(CONCURRENCY_MODE)
            else:
                print_error(f"❌ 無效的 count 設定：{CONCURRENCY_MODE}")
                return ResultCode.INVALID_TASK

            handler = get_handler_by_type(type_key)

            if handler:
                print_info(f"✅ 執行 {type_key} 子控，任務筆數：{len(task_list)}，最大併發數：{count}")
                print_info(f"📄 第一筆任務資料：")
                print(json.dumps(task_list[0], indent=2, ensure_ascii=False))

                result = handler(task_list=task_list, max_concurrency=count)
                error_codes = [code for code in result if code != ResultCode.SUCCESS]

                print_info(f"📦 {type_key} 子控執行完成，錯誤碼列表如下（非 0）：")
                print(error_codes)

                if error_codes:
                    print_error(f"❌ {type_key} 子控有錯誤發生")
                    return ResultCode.TASK_PARTIAL_FAILED

            else:
                print_error(f"❌ 不支援的任務類型：{type_key}")
                return ResultCode.INVALID_TASK

    return ResultCode.SUCCESS
