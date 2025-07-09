"""
任務模組：處理非必要封包（如 websocket/matching 回應）
這些封包不影響流程，但需避免 dispatcher 判定為錯誤。
"""

from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info


async def handle_matching(ws, data):
    """
    伺服器配對中（Start matching...）
    """
    print_info("📡 收到 matching 配對提示封包")
    ws.error_code = ResultCode.SUCCESS
    if hasattr(ws, "callback_done") and not ws.callback_done.is_set():
        ws.callback_done.set()


async def handle_websocket(ws, data):
    """
    WebSocket 成功連線初始化封包
    """
    print_info("🌐 收到 websocket 初始化提示封包")
    ws.error_code = ResultCode.SUCCESS
    if hasattr(ws, "callback_done") and not ws.callback_done.is_set():
        ws.callback_done.set()
