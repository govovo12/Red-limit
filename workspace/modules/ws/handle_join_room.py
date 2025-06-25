import json
from websocket import WebSocketApp
from threading import Event

from workspace.tools.env.config_loader import BET_LEVEL_MODE, BET_AMOUNT_RULE
from workspace.tools.assertion.rule_checker import check_bet_amount_rule
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode

def handle_join_room(ws: WebSocketApp, message: str) -> None:
    print_info("🐛 handle_join_room 被觸發")
    print_info("✅ 收到初始化房間資訊封包（略過封包內容）")

    try:
        packet = json.loads(message)
        if packet.get("event") != "join_room":
            return
        data = packet.get("data", {})
    except Exception as e:
        print_error(f"❌ 封包解析失敗：{e}")
        ws.error_code = ResultCode.TASK_PACKET_PARSE_FAILED
        if hasattr(ws, "callback_done"):
            ws.callback_done.set()
        return

    bet_info = packet.get("bet_info", {})
    if not bet_info:
        print_error("❌ bet_info 不存在")
        ws.error_code = ResultCode.TASK_BET_INFO_INCOMPLETE
        if hasattr(ws, "callback_done"):
            ws.callback_done.set()
        return

    # ✅ 組合下注參數 ctx
    ctx = {}
    for key, value in bet_info.items():
        if isinstance(value, list) and value:
            if key == "bet_level":
                ctx[key] = max(value) if BET_LEVEL_MODE == "max" else min(value)
            else:
                ctx[key] = value[0]
        else:
            ctx[key] = value

    # ✅ 計算 total_bet（自動乘所有可轉 float 的欄位）
    try:
        total_bet = 1
        for key, val in ctx.items():
            try:
                total_bet *= float(val)
            except (TypeError, ValueError):
                continue
        ctx["total_bet"] = total_bet
        print_info(
            f"🔢 總下注金額：{total_bet}（"
            + " * ".join(
                [f"{k}={v}" for k, v in ctx.items()
                 if isinstance(v, (int, float)) or str(v).replace('.', '', 1).isdigit()]
            )
            + "）"
        )
    except Exception as e:
        print_error(f"❌ 無法計算總下注金額：{e}")
        ws.error_code = ResultCode.TASK_TOTAL_BET_CALCULATION_FAILED
        if hasattr(ws, "callback_done"):
            ws.callback_done.set()
        return
    
    ws.bet_context = ctx

    # ✅ 驗證是否符合下注金額規則（來自 .env 設定）
    if not check_bet_amount_rule(BET_AMOUNT_RULE, total_bet):
        print_error(f"❌ 總下注金額 {total_bet} 不符合規則：{BET_AMOUNT_RULE}")
        ws.error_code = ResultCode.TASK_BET_AMOUNT_RULE_VIOLATED
        if hasattr(ws, "callback_done"):
            ws.callback_done.set()
        return
    else:
        print_info("✅ 總下注金額符合規則")

    # ✅ 綁定給下注模組使用
    
    ws.error_code = ResultCode.SUCCESS
