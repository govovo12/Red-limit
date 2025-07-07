# workspace/tools/router/task_dispatcher.py

from workspace.controller.ws.ws_connection_type2_controller import ws_connection_flow as ws_connection_type2_flow
from workspace.controller.ws.ws_connection_type3_controller import ws_connection_flow as ws_connection_type3_flow



TYPE_DISPATCH_MAP = {
    "type_2": ws_connection_type2_flow,
    "type_3": ws_connection_type3_flow,
}

def get_handler_by_type(type_key: str):
    """
    根據 type_key 回傳對應的子控制器 handler。
    若找不到則回傳 None。
    """
    return TYPE_DISPATCH_MAP.get(type_key)
