"""
任務模組（async）：發送 keep_alive 心跳封包，並處理回應

本模組僅回傳錯誤碼，不進行印出，錯誤處理交由子控制器。
"""

# === 標準工具 ===
import json
import asyncio

# === 錯誤碼 ===
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info

async def send_heartbeat_async(ws) -> int:
    print_info("[SEND] 🛰 正在發送 keep_alive 封包")
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


async def handle_heartbeat_response(ws, message: dict) -> None:
    print_info("[Handler] ✅ keep_alive handler 被觸發")

    ws.error_code = ResultCode.SUCCESS

    done = getattr(ws, "callback_done", None)
    if isinstance(done, asyncio.Event):
        if not done.is_set():
            done.set()
            print_info("[Handler] ✅ callback_done 已 set()")
    else:
        print_info("[Handler] ❌ callback_done 未設")




