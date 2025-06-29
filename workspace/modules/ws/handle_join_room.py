# workspace/modules/ws/handle_join_room.py

import json
import threading
from websocket import WebSocketApp

from workspace.tools.env.config_loader import BET_LEVEL_MODE
from workspace.tools.common.result_code import ResultCode


def handle_join_room(ws: WebSocketApp, message: str) -> None:
    """
    任務模組：處理 join_room 封包，解析 bet_info 並綁定下注上下文。
    成功時會印出解析後的 ws.bet_context 結構。
    """
    try:
        packet = json.loads(message)
        event_type = packet.get("event")

        if event_type == "server_error":
            ws.error_code = ResultCode.TASK_JOIN_ROOM_SERVER_ERROR
            return

        if event_type != "join_room":
            return

        bet_info = packet.get("bet_info", {})
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

        # 計算總下注金額
        total_bet = 1
        for val in ctx.values():
            try:
                total_bet *= float(val)
            except (TypeError, ValueError):
                continue
        ctx["total_bet"] = total_bet

        # ✅ 檢查結果是否合法
        if not ctx or ctx.get("total_bet", 0) <= 0:
            ws.error_code = ResultCode.TASK_BET_INFO_INCOMPLETE
            return

        ws.bet_context = ctx
        ws.error_code = ResultCode.SUCCESS

        # ✅ 印出處理後的下注資訊
        print(f"🧾 處理完成的 bet_context：{ctx}")

    except Exception:
        ws.error_code = ResultCode.TASK_PACKET_PARSE_FAILED

    finally:
        if hasattr(ws, "callback_done") and isinstance(ws.callback_done, threading.Event):
            ws.callback_done.set()
