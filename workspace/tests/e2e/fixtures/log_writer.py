# workspace/tests/e2e/fixtures/log_writer.py

from pathlib import Path
from datetime import datetime
from workspace.tools.common.result_code import ResultCode  # ✅ 新增

LOG_DIR = Path("workspace/logs")
ALL_LOG_PATH = LOG_DIR / "all_log.txt"
ERROR_LOG_PATH = LOG_DIR / "error_log.txt"

# ✅ 在模組載入階段就清空（只會執行一次）
LOG_DIR.mkdir(parents=True, exist_ok=True)
ALL_LOG_PATH.write_text("", encoding="utf-8")
ERROR_LOG_PATH.write_text("", encoding="utf-8")

def log_writer():
    def write(result: dict):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        oid = result.get("oid", "?")
        error_code = result.get("error_code", "?")
        expected = result.get("expected", "-")
        actual = result.get("actual", "-")

        # ✅ 自動列出所有下注參數（包含 bet_ 開頭與 total_bet）
        param_str = " * ".join([
            f"{k}={v}" for k, v in result.items()
            if k.startswith("bet_") or k == "total_bet"
        ]) or "無下注參數"

        # ✅ 加入錯誤類型標籤（依錯誤碼）
        error_type = {
            ResultCode.TASK_BET_AMOUNT_RULE_VIOLATED: "限紅錯誤",
            ResultCode.TASK_BET_MISMATCHED: "金額不一致",
            ResultCode.TASK_TOTAL_BET_CALCULATION_FAILED: "計算錯誤",
            ResultCode.TASK_PACKET_PARSE_FAILED: "封包錯誤",
        }.get(error_code, "其他錯誤")

        msg = f"[{error_type}] OID={oid} ({param_str}) 預期={expected}，實際={actual}"

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(ALL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
        if error_code != 0:
            with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {msg}\n")

    return write
