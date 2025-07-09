"""
任務模組（async）：發送 keep_alive 心跳封包，並處理回應

本模組僅回傳錯誤碼，不進行印出，錯誤處理交由子控制器。
"""

# === 標準工具 ===
import json
import asyncio

# === 錯誤碼 ===
from workspace.tools.common.result_code import ResultCode


async def send_heartbeat_async(ws) -> int:
    """
    傳送 keep_alive 封包

    Args:
        ws: WebSocket 連線物件

    Returns:
        int: ResultCode.SUCCESS 或錯誤碼
    """
    try:
        await ws.send(json.dumps({"event": "keep_alive"}))
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_SEND_HEARTBEAT_FAILED


def handle_heartbeat_response(ws, message: dict) -> None:
    """
    預設處理 keep_alive 回應（不做額外驗證，只設為完成）

    Args:
        ws: WebSocket 物件
        message (dict): 回應封包
    """
    ws.error_code = ResultCode.SUCCESS  # ✅ 加上這行才不會被當成錯誤！

    if hasattr(ws, "callback_done"):
        ws.callback_done.set()
