from concurrent.futures import ThreadPoolExecutor
from workspace.modules.batch.prepare_oid_list_by_type import get_oid_list_by_type
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info, print_error
import json

def run_type_ws_tasks(task_bundle: dict):
    """
    執行指定 type 的 WebSocket 測試任務。
    """
    game_type = task_bundle["type"]
    task_list = task_bundle["data"].get(game_type, [])
    count = task_bundle.get("count", len(task_list))

    if not task_list:
        print_info(f"[DEV] ⚠️ 無可用的 {game_type} 任務，跳過執行")
        return

    # ✅ 印出子控接收到的任務包資訊（確認結構）
    game_type = task_bundle["type"]
    task_list = task_bundle["data"].get(game_type, [])
    print_info(f"[DEV] ✅ 子控接收到的任務包：type = {game_type}, count = {task_bundle.get('count')}")
    if task_list:
        print_info("[DEV] 📄 第一筆任務資料內容如下（含巢狀結構）：")
        print(json.dumps(task_list[0], indent=2, ensure_ascii=False))


def run_ws_batch_dev(game_type: str):
    """
    任務 009 子控制器：處理單一 type 或 ALL 類型的任務流程。
    """
    print_info(f"[DEV] 🎮 開始執行 {game_type} 任務流程")

    code, result = get_oid_list_by_type(game_type)

    if code != ResultCode.SUCCESS:
        print_error(f"[DEV] ❌ 無法取得 OID 資料，錯誤碼：{code}")
        return

    if game_type == "ALL":
        for _, bundle in result.items():
            run_type_ws_tasks(bundle)
    else:
        run_type_ws_tasks(result)
