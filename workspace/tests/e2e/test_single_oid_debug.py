# workspace/tests/e2e/test_single_oid_debug.py

import pytest
from workspace.tools.common.result_code import ResultCode
from workspace.tests.e2e.utils.log_formatter import print_bet_error
from workspace.tests.e2e.fixtures.bet_validation_fixture import run_ws_bet_flow
from workspace.controller.login.r88_login_controller import r88_login_flow

pytestmark = [pytest.mark.e2e, pytest.mark.betting]

@pytest.mark.parametrize("account, oid", [
    ("qa0002", "307"),
])
def test_single_oid_bet_debug(account, oid, log_writer_fixture):
    """
    單一 OID 測試（不中斷流程，但收到錯誤碼即 fail），適用新版子控邏輯。
    並透過 fixture 統一寫入 log。
    """
    # 🔐 確保登入成功（刷新快取與 token）
    login_code = r88_login_flow(account)
    assert login_code == ResultCode.SUCCESS, f"登入失敗，錯誤碼：{login_code}"

    # 🧪 執行 WebSocket 子控流程
    result = run_ws_bet_flow(account=account, oid=oid)
    print("🧪 result =", result)

    # 🗂️ 寫入 log（與多筆測試一致）
    log_writer_fixture(result)

    # ⚠️ 若 error_code 不是 SUCCESS，一律視為錯誤
    if result["error_code"] != ResultCode.SUCCESS:
        print_bet_error(result)
        pytest.fail(f"❌ 子控制器回傳錯誤碼：{result['error_code']}")

    # 🧮 若金額比對不符，也視為錯誤（補充保險機制）
    if result["expected"] != result["actual"]:
        print_bet_error(result)
        pytest.fail(f"❌ 金額不一致：{result['expected']} ≠ {result['actual']}")
