import json
from workspace.tools.common.result_code import ResultCode


async def send_exit_room_async(ws) -> int:
    """
    發送 exit_room 封包（async），不驗回傳內容。
    發送失敗則回傳 TASK_EXCEPTION。
    """
    try:
        payload = {"event": "exit_room"}
        await ws.send(json.dumps(payload))
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_EXCEPTION


async def handle_exit_room_ack(ws, message: str) -> None:
    """
    收到 exit_room 回應的 handler（async），不驗內容。
    只要收到封包就 callback_done。
    """
    if hasattr(ws, "callback_done"):
        ws.callback_done.set()
