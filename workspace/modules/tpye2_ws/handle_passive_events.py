# 處理不重要的被動事件封包（僅印出，不設錯誤碼 / callback）
from workspace.tools.printer.printer import print_info


def handle_matching(ws, data):
    """
    被動封包：matching（配對提示）
    """
    print_info("📡 收到 matching 配對提示封包")


def handle_websocket(ws, data):
    """
    被動封包：websocket 初始化提示
    """
    print_info("🌐 收到 websocket 初始化提示封包")
