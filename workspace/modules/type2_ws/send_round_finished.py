"""
任務模組（async）：發送 cur_round_finished 封包並處理回應
"""

# === 標準工具 ===
import json

# === 錯誤碼 ===
from workspace.tools.common.result_code import ResultCode


async def send_round_finished_async(ws) -> int:
    """
    發送 cur_round_finished 封包（async）。
    不驗回傳內容，成功回傳 SUCCESS，失敗回傳對應錯誤碼。

    Args:
        ws: WebSocket 連線物件

    Returns:
        int: ResultCode
    """
    try:
        payload = {"event": "cur_round_finished"}
        payload_str = json.dumps(payload)
        await ws.send(payload_str)
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_SEND_ROUND_FINISHED_FAILED


async def handle_round_finished_ack(ws, message: dict):
    ws.error_code = ResultCode.SUCCESS
    if hasattr(ws, "callback_done"):
        ws.callback_done.set()

