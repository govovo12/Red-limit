"""
提供 callback_done 的安全觸發工具
"""

def callback_done(ws):
    """
    安全地觸發 ws.callback_done.set()，若未註冊該屬性則略過。

    用於子控流程中各任務模組處理封包完成時通知主流程。
    """
    if hasattr(ws, "callback_done") and ws.callback_done:
        ws.callback_done.set()
