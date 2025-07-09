"""
任務模組（async）：處理 join_room 封包，解析 bet_info 並綁定下注上下文。

成功時設定 ws.bet_context 與 ws.error_code。不印 log。
"""

# === 錯誤碼與模組 ===
import asyncio
from workspace.tools.env.config_loader import BET_LEVEL_MODE
from workspace.tools.common.result_code import ResultCode


async def handle_join_room_async(ws, message: dict) -> None:
    """
    處理 join_room 封包內容，並將解析結果綁定至 ws 物件。
    若成功則設定 ws.bet_context 與 SUCCESS 錯誤碼，否則設定對應錯誤碼。

    Args:
        ws (Any): WebSocket 對象（會設定 error_code 與 bet_context）
        message (dict): 接收到的封包資料
    """
    try:
        if getattr(ws, "error_code", None) == ResultCode.SUCCESS:
            return

        event_type = message.get("event")
        if event_type == "server_error":
            ws.error_code = ResultCode.TASK_JOIN_ROOM_SERVER_ERROR
            return

        if event_type != "join_room":
            ws.error_code = ResultCode.TASK_JOIN_ROOM_EVENT_MISMATCH
            ws.raw_packet = message  # 讓子控可印出
            return

        bet_info = message.get("bet_info", {})
        if not bet_info or not isinstance(bet_info, dict):
            ws.error_code = ResultCode.TASK_BET_INFO_INCOMPLETE
            return

        ctx = {}
        for key, value in bet_info.items():
            if value is None:
                continue
            if isinstance(value, list) and value:
                ctx[key] = max(value) if (key == "bet_level" and BET_LEVEL_MODE == "max") else min(value)
            else:
                ctx[key] = value

        total_bet = 1
        for val in ctx.values():
            try:
                total_bet *= float(val)
            except (TypeError, ValueError):
                continue
        ctx["total_bet"] = total_bet

        if not ctx or ctx.get("total_bet", 0) <= 0:
            ws.error_code = ResultCode.TASK_BET_INFO_INCOMPLETE
            return

        ws.bet_context = ctx
        ws.error_code = ResultCode.SUCCESS

    except Exception:
        ws.error_code = ResultCode.TASK_PACKET_PARSE_FAILED

    finally:
        if hasattr(ws, "callback_done") and isinstance(ws.callback_done, asyncio.Event):
            if not ws.callback_done.is_set():
                ws.callback_done.set()
