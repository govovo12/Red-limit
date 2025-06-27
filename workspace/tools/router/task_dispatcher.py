# workspace/tools/router/task_dispatcher.py

from workspace.controller.ws.ws_connection_controller import ws_connection_flow
# 預留：未來可以加入更多 type 對應的子控制器
# from workspace.controller.http.http_controller import http_flow
# from workspace.controller.bot.bot_controller import bot_flow

TYPE_DISPATCH_MAP = {
    "type_2": ws_connection_flow,
    # "type_1": http_flow,
    # "type_3": bot_flow,
}

def get_handler_by_type(type_key: str):
    """
    根據 type_key 回傳對應的子控制器 handler。
    若找不到則回傳 None。
    """
    return TYPE_DISPATCH_MAP.get(type_key)
