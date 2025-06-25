import time
from workspace.tools.file.data_loader import load_json
from workspace.config.paths import get_oid_list_path
from workspace.controller.ws.ws_connection_controller import ws_connection_flow
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode


def run_ws_for_all_oids(account: str = "qa0002") -> int:
    """
    逐一執行 ws_connection_flow() 對所有 OID 建立 WebSocket 測試流程。

    Args:
        account (str): 登入帳號（預設為 "qa0002"）

    Returns:
        int: 統一回傳任務成功或錯誤碼（ResultCode）
    """
    code, oid_list = load_json(get_oid_list_path())
    if code != ResultCode.SUCCESS or not oid_list:
        print_error("❌ 無法讀取 OID 清單")
        return ResultCode.TASK_SINGLE_WS_OID_LIST_EMPTY

    print_info(f"📋 共 {len(oid_list)} 筆 OID，準備逐一測試")

    for idx, oid in enumerate(oid_list, 1):
        print_info(f"\n==== 🚀 [{idx}/{len(oid_list)}] 測試 OID：{oid} ====")
        start = time.time()
        result = ws_connection_flow(account=account, oid=str(oid))
        elapsed = round(time.time() - start, 2)

        if result != ResultCode.SUCCESS:
            print_error(f"❌ OID {oid} 測試失敗（錯誤碼：{result}），耗時 {elapsed}s")
        else:
            print_info(f"✅ OID {oid} 測試成功，耗時 {elapsed}s")

    print_info("\n🎯 所有 OID 測試流程已完成")
    return ResultCode.SUCCESS


if __name__ == "__main__":
    run_ws_for_all_oids()
