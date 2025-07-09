# handle_join_room_async.py

import asyncio
from workspace.tools.common.result_code import ResultCode
from workspace.tools.env.config_loader import BET_LEVEL_MODE


async def handle_join_room_async(ws, message: dict) -> None:
    try:
        # 檢查事件名稱是否為 join_room
        if message.get("event") != "join_room":
            ws.error_code = ResultCode.TASK_JOIN_ROOM_EVENT_MISMATCH
            ws.raw_packet = message
            print(f"❌ 接收到非 join_room 事件: {message.get('event')}")
            return

        # 檢查 bet_info 是否存在且格式正確
        bet_info = message.get("bet_info", {})
        if not bet_info or not isinstance(bet_info, dict):
            ws.error_code = ResultCode.TASK_BET_INFO_INCOMPLETE
            print(f"❌ bet_info 不完整或格式錯誤: {bet_info}")
            return

        ctx = {}
        for key, value in bet_info.items():
            if value is None:
                continue
            if isinstance(value, list) and value:
                ctx[key] = max(value) if (key == "bet_level" and BET_LEVEL_MODE == "max") else min(value)
            else:
                ctx[key] = value

        # 計算 total_bet
        total_bet = 1
        for val in ctx.values():
            try:
                total_bet *= float(val)
            except Exception:
                continue

        ctx["total_bet"] = total_bet
        ws.bet_context = ctx

        # 只有在解析成功後設置 SUCCESS
        ws.error_code = ResultCode.SUCCESS
        print(f"[join_room] ✔ 成功解析 bet context: {ctx}")

    except Exception as e:
        ws.error_code = ResultCode.TASK_PACKET_PARSE_FAILED
        print(f"❌ 解析過程中出現錯誤: {e}")

    finally:
        # 確保只有 join_room 事件設置 _join_event
        if getattr(ws, "_join_event", None) and isinstance(ws._join_event, asyncio.Event):
            if not ws._join_event.is_set():
                ws._join_event.set()





