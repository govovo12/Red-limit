# workspace/tests/e2e/test_bet_amount_validation.py

import pytest
from workspace.tools.common.result_code import ResultCode
from workspace.tests.e2e.utils.log_formatter import print_bet_error

pytestmark = [pytest.mark.e2e, pytest.mark.betting]

@pytest.mark.parametrize("account", ["qa0002"])
def test_all_oid_bet_amount_validation(account, oid_list, run_bet_flow, log_writer_fixture):
    """
    執行所有 OID 的下注流程，不中斷，記錄所有錯誤，最後統一報錯。
    接入新版錯誤分類邏輯。
    """
    errors = []

    for oid in oid_list:
        result = run_bet_flow(account=account, oid=str(oid))
        log_writer_fixture(result)

        if result["error_code"] != ResultCode.SUCCESS:
            print_bet_error(result)
            errors.append(result)

    assert not errors, f"❌ 共 {len(errors)} 筆失敗，請檢查 error_log.txt"
