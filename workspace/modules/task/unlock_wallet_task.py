"""
任務模組：解鎖錢包
使用 pf_account 發送解鎖 API
"""

# === 標準工具 ===
from workspace.tools.network.request_handler import safe_post
from workspace.tools.common.result_code import ResultCode
from workspace.tools.env.config_loader import R88_UNLOCK_WALLET_URL

async def unlock_wallet(pf_account: str) -> int:
    """
    使用 pf_account 發送解鎖請求。
    """
    try:
        payload = {"id": pf_account}
        response = safe_post(R88_UNLOCK_WALLET_URL, json=payload)
        res_json = response.json()
        if res_json.get("code") == 0:
            return ResultCode.SUCCESS
        return ResultCode.TASK_UNLOCK_WALLET_FAILED
    except Exception:
        return ResultCode.TASK_UNLOCK_WALLET_EXCEPTION
