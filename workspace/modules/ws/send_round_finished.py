import json
from workspace.tools.common.result_code import ResultCode


async def send_round_finished_async(ws) -> int:
    """
    發送 cur_round_finished 封包（async）。
    不驗回傳內容，成功回傳 SUCCESS，失敗回傳 TASK_EXCEPTION。
    """
    try:
        payload = {"event": "cur_round_finished"}
        payload_str = json.dumps(payload)
        await ws.send(payload_str)
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_EXCEPTION


async def handle_round_finished_ack(ws, message: str) -> None:
    """
    收到 cur_round_finished 回應的 handler（async），不驗內容。
    """
    if hasattr(ws, "callback_done"):
        ws.callback_done.set()
