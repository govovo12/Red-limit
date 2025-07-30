from workspace.controller.login.r88_login_controller import r88_login_flow
from workspace.controller.batch.ws_batch_controller_dev import run_ws_batch_dev
from workspace.tools.router.task_dispatcher import get_handler_by_type
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.log_helper import log_step_result
from workspace.tools.common.result_code import ResultCode
from workspace.tools.env.config_loader import TASK_LIST_MODE, CONCURRENCY_MODE
from workspace.tools.printer.progress_reporter import report_progress  # ✅ 新增
import json
from workspace.modules.task.write_ws_flow_log import init_log_file, write_log


def run_main_flow(task: str, game_type: str = None) -> int:
    if task == "001":
        report_progress(10, "🔐 登入中...")
        r88_login_flow("qa0002")
        report_progress(100, "✅ 登入完成")
        return ResultCode.SUCCESS

    elif task == "009":
        if not game_type:
            print_error("❌ 請指定 --type（例如 type_2 或 ALL）")
            return ResultCode.INVALID_TASK

        report_progress(10, "📥 正在取得任務資料...")
        task_dict = run_ws_batch_dev(game_type)
        report_progress(30, "🧾 任務分派完成")
        print_info("🧩 任務 009 結果如下：")
        print(json.dumps(task_dict, indent=2, ensure_ascii=False))
        report_progress(100, "✅ 任務執行完成")
        return ResultCode.SUCCESS

    elif task == "001+009":
        report_progress(10, "🔐 登入中...")
        r88_login_flow("qa0002")

        if not game_type:
            print_info("ℹ️ 未指定 --type，僅執行登入與 access_token，未執行任何子控流程")
            report_progress(100, "✅ 登入完成")
            return ResultCode.SUCCESS

        report_progress(20, "📥 取得任務資料中...")
        if game_type == "ALL":
            all_types = ["type_1", "type_2", "type_3"]
            combined_task_dict = {}

            for t in all_types:
                sub_dict = run_ws_batch_dev(t)
                if sub_dict and t in sub_dict:
                    print_info(f"[DEBUG] sub_dict ({t}) 回傳結構：")
                    print(json.dumps(sub_dict, indent=2, ensure_ascii=False))
                    combined_task_dict[t] = sub_dict[t]
                    count = len(sub_dict[t].get("data", {}).get(t, []))
                    print_info(f"[DEBUG] ✅ 成功抓到 {t} 任務，共 {count} 筆")
                else:
                    print_info(f"[DEBUG] ⚠️ 無任務資料：{t}")

            task_dict = combined_task_dict
        else:
            task_dict = run_ws_batch_dev(game_type)

        print_info("🧩 總控接收到的完整任務 dict 結構如下：")
        print(json.dumps(task_dict, indent=2, ensure_ascii=False))
        report_progress(40, "🧾 任務準備完成，準備執行子控...")

        for type_key, bundle in task_dict.items():
            data_list = bundle["data"][type_key]
            for task in data_list:
                task["type"] = type_key

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
                report_progress(60, f"🎮 執行子控流程：{type_key}...")
                print_info(f"✅ 執行 {type_key} 子控，任務筆數：{len(task_list)}，最大併發數：{count}")
                print_info(f"📄 第一筆任務資料：")
                print(json.dumps(task_list[0], indent=2, ensure_ascii=False))

                result = handler(task_list=task_list, max_concurrency=count)

                for line in result:
                    if isinstance(line, str) and line.startswith("type_"):
                        type_key = line.split(":")[0].strip()
                        init_log_file(type_key)
                        write_log(line, timestamp=False)

                    elif isinstance(line, int) and line != ResultCode.SUCCESS:
                        print_error(f"❌ 子控回傳錯誤碼：{line}")

                error_codes = [code for code in result if isinstance(code, int) and code not in {
                    ResultCode.SUCCESS, ResultCode.TASK_BET_AMOUNT_VIOLATED}]

                print_info(f"📦 {type_key} 子控執行完成，錯誤碼列表如下（非 0）：")
                print(error_codes)

                if error_codes:
                    print_error(f"❌ {type_key} 子控有錯誤發生")
                    report_progress(90, f"⚠️ 子控錯誤：{type_key}")
                    return ResultCode.TASK_PARTIAL_FAILED
            else:
                print_error(f"❌ 不支援的任務類型：{type_key}")
                return ResultCode.INVALID_TASK

        report_progress(100, "✅ 所有流程完成")

    return ResultCode.SUCCESS
