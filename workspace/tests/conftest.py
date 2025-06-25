# workspace/tests/conftest.py

import pytest
from workspace.tests.e2e.fixtures.bet_validation_fixture import run_ws_bet_flow
from workspace.tests.e2e.fixtures.log_writer import log_writer

@pytest.fixture(scope="session")
def oid_list():
    from workspace.controller.login.r88_login_controller import r88_login_flow
    from workspace.tools.file.data_loader import load_json
    from workspace.config.paths import get_oid_list_path

    # ✅ 明確登入，不透過 run_task_001（避免快取判斷失誤）
    login_code = r88_login_flow("qa0002")
    assert login_code == 0, f"登入失敗，錯誤碼：{login_code}"

    code, oids = load_json(get_oid_list_path())
    assert code == 0 and oids, "OID 清單讀取失敗"
    return oids

@pytest.fixture
def run_bet_flow():
    return run_ws_bet_flow

@pytest.fixture
def log_writer_fixture():
    return log_writer()
