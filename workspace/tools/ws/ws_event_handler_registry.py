# ws_event_handler_registry.py

# === Type2 專用事件 handler ===
from workspace.modules.type2_ws.handle_join_room_async import handle_join_room_async
from workspace.modules.type2_ws.send_heartbeat_task import handle_heartbeat_response
from workspace.modules.type2_ws.parse.parse_bet_response import handle_bet_ack
from workspace.modules.type2_ws.send_round_finished import handle_round_finished_ack
from workspace.modules.type2_ws.send_exit_room import handle_exit_room_ack
# === Type3 專用事件 handler ===
from workspace.modules.type3_ws.verify_init_info_type3 import handle_init_info

# === Dispatcher ===
from workspace.tools.ws.ws_event_dispatcher_async import register_event_handler
from workspace.tools.printer.printer import print_info, print_error

# ✅ 巢狀註冊表：flow_type → {event_name → handler}
event_handler_registry = {
    "type2": {
        "join_room": handle_join_room_async,
        "keep_alive": handle_heartbeat_response,
        "bet": handle_bet_ack,
        "cur_round_finished": handle_round_finished_ack,
        # exit_room 改為 global 共用
    },
    "type3": {
        "init_info": handle_init_info,
        # exit_room 共用 global，不放這裡
    },
    "global": {
        "exit_room": handle_exit_room_ack,
    }
}


def auto_register_event_handlers(ws, flow_type: str):
    """
    根據 flow_type 從註冊表載入所有事件 handler，並註冊到 dispatcher。
    預設會先註冊 global，再註冊特定 flow_type 的事件。
    """
    total = 0

    for scope in ("global", flow_type):
        handlers = event_handler_registry.get(scope, {})
        for event, handler in handlers.items():
            register_event_handler(ws, event, handler)
            print_info(f"[Bind-{scope}] event='{event}' → handler='{handler.__name__}'")
            total += 1

    if total == 0:
        print_error(f"[Warning] flow_type='{flow_type}' 沒有任何事件綁定")
