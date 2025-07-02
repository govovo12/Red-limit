# workspace/modules/ws/send_heartbeat_task.py

"""
任務模組（async）：發送心跳封包並處理回應
"""

import json
from workspace.tools.printer.printer import print_info
from workspace.tools.common.result_code import ResultCode


async def send_heartbeat_async(ws) -> int:
    """
    發送心跳封包（keep_alive），使用 async WebSocket 客戶端。
    子控需先註冊好 callback 並設置 ws.callback_done。
    """
    try:
        await ws.send(json.dumps({"event": "keep_alive"}))
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_SEND_HEARTBEAT_FAILED


def handle_heartbeat_response(ws, message: dict) -> None:
    """
    處理 keep_alive 回應封包（僅確認有回應，不驗內容）。
    若 ws 有設 callback_done，立即觸發完成。
    """
    print_info("✅ 收到 keep_alive 回應（不驗內容）")
    if hasattr(ws, "callback_done"):
        ws.callback_done.set()
