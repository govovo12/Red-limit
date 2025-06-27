import json
from websocket import WebSocketApp
from threading import Event
from workspace.tools.env.config_loader import BET_LEVEL_MODE
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode

def handle_join_room(ws: WebSocketApp, message: str) -> None:
    print_info("🐛 handle_join_room 被觸發")
    print_info("✅ 收到初始化房間資訊封包（略過封包內容）")

    # 解析封包，捕獲解析錯誤
    try:
        packet = json.loads(message)
        if packet.get("event") != "join_room":
            return  # 如果不是 join_room 事件，則不處理
        data = packet.get("data", {})
    except Exception as e:
        print_error(f"❌ 封包解析失敗：{e}")
        ws.error_code = ResultCode.TASK_PACKET_PARSE_FAILED
        if hasattr(ws, "callback_done"):
            ws.callback_done.set()  # 確保錯誤後結束
        return

    # 確保 bet_info 存在
    bet_info = packet.get("bet_info", {})
    if not bet_info:
        print_error("❌ bet_info 不存在")
        ws.error_code = ResultCode.TASK_BET_INFO_INCOMPLETE
        if hasattr(ws, "callback_done"):
            ws.callback_done.set()  # 返回錯誤並結束
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
                continue  # 當值無法轉為數字時跳過
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
            ws.callback_done.set()  # 結束並返回錯誤
        return

    # ✅ 綁定給下注模組使用
    ws.bet_context = ctx
    ws.error_code = ResultCode.SUCCESS

    if hasattr(ws, "callback_done"):
        ws.callback_done.set()  # 確保處理完成
