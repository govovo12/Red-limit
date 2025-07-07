from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_info


async def handle_init_info(ws, message: dict):
    """
    Type 3 用任務模組：處理伺服器回傳的 init_info 封包，
    目前改為：僅接收完整封包並暫存，回傳給子控處理。
    """
    try:
        print_info("🧩 [DEBUG] 進入 handle_init_info()")
        print_info(f"🧩 [封包內容] {message}")

        # Step 3: 儲存完整封包供子控後續處理
        ws.rs_data = message

        # 回報成功並結束 callback
        ws.error_code = ResultCode.SUCCESS
        ws.callback_done.set()

    except Exception as e:
        print_info(f"[ERROR] 任務模組例外: {e}")
        ws.error_code = ResultCode.TASK_EXCEPTION
        ws.callback_done.set()
