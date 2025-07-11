import asyncio
from workspace.tools.common.result_code import ResultCode
from workspace.tools.env.config_loader import BET_LEVEL_MODE


async def handle_join_room_async(ws, message: dict) -> None:
    try:
        # ✅ 僅處理 join_room 封包
        if message.get("event") != "join_room":
            ws.error_code = ResultCode.TASK_JOIN_ROOM_EVENT_MISMATCH
            ws.raw_packet = message  # 🔍 保存異常封包
            return

        # ✅ 確保 bet_info 存在且為 dict
        bet_info = message.get("bet_info", {})
        if not isinstance(bet_info, dict) or not bet_info:
            ws.error_code = ResultCode.TASK_BET_INFO_INCOMPLETE
            return

        # ✅ 擷取下注參數
        ctx = {}
        for key, value in bet_info.items():
            if value is None:
                continue
            if isinstance(value, list) and value:
                ctx[key] = max(value) if (key == "bet_level" and BET_LEVEL_MODE == "max") else min(value)
            else:
                ctx[key] = value

        # ✅ 計算總下注金額
        total_bet = 1
        for val in ctx.values():
            try:
                total_bet *= float(val)
            except Exception:
                continue

        ctx["total_bet"] = total_bet
        ws.bet_context = ctx
        

        # ✅ 一切成功
        ws.error_code = ResultCode.SUCCESS

    except Exception:
        ws.error_code = ResultCode.TASK_PACKET_PARSE_FAILED
        ws.raw_packet = message  # 🔍 捕捉失敗時封包

    finally:
        # ✅ 通知主流程處理完成
        if getattr(ws, "_join_event", None) and isinstance(ws._join_event, asyncio.Event):
            if not ws._join_event.is_set():
                ws._join_event.set()
