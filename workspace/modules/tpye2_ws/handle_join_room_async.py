# handle_join_room_async.py

import asyncio
from workspace.tools.common.result_code import ResultCode
from workspace.tools.env.config_loader import BET_LEVEL_MODE


async def handle_join_room_async(ws, message: dict) -> None:
    try:
        
        # 僅處理 join_room 封包
        if message.get("event") != "join_room":
            ws.error_code = ResultCode.TASK_JOIN_ROOM_EVENT_MISMATCH
            ws.raw_packet = message
            
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
            except Exception:
                continue

        ctx["total_bet"] = total_bet
        ws.bet_context = ctx

        ws.error_code = ResultCode.SUCCESS
 

        
        if getattr(ws, "_join_event", None) and isinstance(ws._join_event, asyncio.Event):
            if not ws._join_event.is_set():
                ws._join_event.set()
                

    except Exception as e:
        ws.error_code = ResultCode.TASK_PACKET_PARSE_FAILED
        print(f"❌ 解析過程中出現錯誤: {e}")
        # ❌ 不應 set _join_event，在錯誤狀況下流程應中止






