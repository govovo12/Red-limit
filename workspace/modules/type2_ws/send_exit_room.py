"""
任務模組（async）：發送 exit_room 封包並處理回應
"""

# === 標準工具 ===
import json

# === 錯誤碼 ===
from workspace.tools.common.result_code import ResultCode


async def send_exit_room_async(ws) -> int:
    """
    發送 exit_room 封包（async），不驗回傳內容。

    Args:
        ws: WebSocket 連線物件

    Returns:
        int: ResultCode
    """
    try:
        payload = {"event": "exit_room"}
        payload_str = json.dumps(payload)
        await ws.send(payload_str)
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_SEND_EXIT_ROOM_FAILED


async def handle_exit_room_ack(ws, message: str) -> None:
    """
    收到 exit_room 回應的 handler（async），不驗內容。
    """
    if hasattr(ws, "callback_done") and ws.callback_done.is_set():
       return
    ws.error_code = ResultCode.SUCCESS  # ✅ 補這一行
    if hasattr(ws, "callback_done"):
        ws.callback_done.set()