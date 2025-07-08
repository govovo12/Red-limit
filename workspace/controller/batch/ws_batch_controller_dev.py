from concurrent.futures import ThreadPoolExecutor
import json

from workspace.modules.batch.prepare_oid_list_by_type import get_oid_list_by_type  # ✅ 任務 009-A
from workspace.modules.batch.generate_account_oid_pairs import generate_account_oid_pairs  # ✅ 任務 009-B
from workspace.modules.batch.login_task import run_login_task  # ✅ 任務 009-C
from workspace.modules.batch.get_access_token_task import get_access_token_task  # ✅ 任務 009-D

from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info
from workspace.tools.common.log_helper import log_step_result


def run_type_ws_tasks(task_bundle: dict):
    """
    任務 009 子控流程：執行指定 type 的 WebSocket 任務。
    任務階段：
      - 009-B：加入帳號欄位
      - 009-C：登入並寫入 lobby_token（併發）
      - 009-D：取得 access_token（併發，並移除 lobby_token）
    """
    game_type = task_bundle["type"]
    task_list = task_bundle["data"].get(game_type, [])
    count = task_bundle.get("count", len(task_list))

    if not task_list:
        print_info(f"[DEV] ⚠️ 無可用的 {game_type} 任務，跳過執行")
        return

    print_info(f"[DEV] ✅ 任務類型：{game_type}，原始任務筆數：{count}")
    print_info("[DEV] 📄 原始第一筆任務資料：")
    print(json.dumps(task_list[0], indent=2, ensure_ascii=False))

    # ✅ 任務 009-B：加入帳號欄位
    task_list, code = generate_account_oid_pairs(task_list)
    if code != ResultCode.SUCCESS:
        log_step_result(code, step="generate_account_oid_pairs")
        return
    print_info(f"[DEV] ✅ 完成帳號配對，共 {len(task_list)} 組")
    print_info("[DEV] 📄 加入帳號後第一筆任務資料：")
    print(json.dumps(task_list[0], indent=2, ensure_ascii=False))

    # ✅ 任務 009-C：登入 API（取得 lobby_token）
    success_count = 0
    fail_count = 0
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(run_login_task, task) for task in task_list]
        for i, future in enumerate(futures):
            code = future.result()
            if code == ResultCode.SUCCESS:
                success_count += 1
            else:
                fail_count += 1
                log_step_result(code, step="login_task", account=task_list[i]["account"])

    print_info(f"[DEV] ✅ 登入任務完成：成功 {success_count} 筆，失敗 {fail_count} 筆")
    print_info("[DEV] 📄 登入後第一筆任務資料（含 lobby_token）：")
    print(json.dumps(task_list[0], indent=2, ensure_ascii=False))

    # ✅ 任務 009-D：取得 access_token（並移除 lobby_token）
    updated_list = []
    success_count = 0
    fail_count = 0
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(get_access_token_task, task) for task in task_list]
        for i, future in enumerate(futures):
            new_task, code = future.result()
            updated_list.append(new_task)
            if code == ResultCode.SUCCESS:
                success_count += 1
            else:
                fail_count += 1
                log_step_result(code, step="get_access_token", account=new_task.get("account"))

    print_info(f"[DEV] ✅ access_token 任務完成：成功 {success_count} 筆，失敗 {fail_count} 筆")
    print_info("[DEV] 📄 access_token 後第一筆任務資料（應不含 lobby_token）：")
    print(json.dumps(updated_list[0], indent=2, ensure_ascii=False))

    # ✅ 組裝結果
    task_bundle["data"][game_type] = updated_list
    task_bundle["count"] = len(updated_list)


def run_ws_batch_dev(game_type: str) -> dict:
    """
    任務 009 子控制器：執行完整流程，從 009-A 取得 OID 清單開始。
    回傳格式：{type_key: bundle}
    """
    print_info(f"[DEV] 🎮 開始執行 {game_type} 任務流程")

    # ✅ 任務 009-A：讀取巢狀 OID 清單
    code, result = get_oid_list_by_type(game_type)
    if code != ResultCode.SUCCESS:
        log_step_result(code, step="get_oid_list_by_type")
        return {}

    # ✅ 任務 009-B ~ 009-D：處理每個 type 的任務
    if game_type == "ALL":
        final_result = {}
        for type_key, bundle in result.items():
            run_type_ws_tasks(bundle)
            final_result[type_key] = bundle
        return final_result
    else:
        run_type_ws_tasks(result)
        return {result["type"]: result}
