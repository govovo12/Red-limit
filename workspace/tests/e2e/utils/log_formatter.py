# workspace/tests/e2e/utils/log_formatter.py

from workspace.tools.common.result_code import ResultCode

def print_bet_error(result: dict) -> None:
    """
    印出下注錯誤詳細資訊，包含 OID、下注參數、expected / actual。
    支援動態下注參數（以 bet_ 開頭或 total_bet）。
    """
    if result.get("error_code") == ResultCode.SUCCESS:
        return

    print("\n❌ [下注金額驗證失敗]")
    print(f"→ OID: {result.get('oid')} | 帳號: {result.get('account')}")
    print(f"→ 預期金額: {result.get('expected')}，實際金額: {result.get('actual')}")

    # ✅ 自動列出所有下注參數（包含 bet_ 開頭與 total_bet）
    param_str = " * ".join([
        f"{k}={v}" for k, v in result.items()
        if (k.startswith("bet_") or k == "total_bet") and v is not None
    ]) or "無下注參數"

    print(f"→ 下注參數: {param_str}")
