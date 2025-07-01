# workspace/config/rules/result_code.py

# ✅ 錯誤碼定義模組
# ✅ 分類規則：
#   - 0 為成功
#   - 10000～10199：WebSocket 任務模組錯誤
#   - 40000～        工具模組錯誤
#   - 其他為保留或未分類錯誤
# ✅ 配套字典：
#   - SUCCESS_CODES / TOOL_ERROR_CODES / TASK_ERROR_CODES / GENERIC_ERROR_CODES
#   - ERROR_MESSAGES（用於 log_simple_result 印出訊息）

class ResultCode:
    # ✅ 成功
    SUCCESS = 0
    # -------------------------------
    # ✅ Batch(組合前置資料任務) 任務錯誤碼（600-700）
    # -------------------------------
     # OID 任務錯誤
    TASK_OID_LIST_FOR_TYPE_NOT_FOUND = 600  # 指定 type 的 OID 清單不存在



    # -------------------------------
    # ✅ WebSocket 任務錯誤碼（10000～10199）
    # -------------------------------

    # 建立連線與事件等待
    TASK_WS_CONNECTION_FAILED = 10010
    TASK_WS_CONNECTION_LOST = 10011
    TASK_CONNECT_WS_FAILED = 10012
    TASK_CALLBACK_TIMEOUT = 10013

    # join_room
    TASK_BET_INFO_INCOMPLETE = 10020
    TASK_TOTAL_BET_CALCULATION_FAILED = 10021
    TASK_JOIN_ROOM_SERVER_ERROR = 10022
    TASK_BET_CONTEXT_MISSING = 10023
    TASK_PACKET_PARSE_FAILED = 10050

    # keep_alive
    TASK_SEND_HEARTBEAT_FAILED = 10030
    TASK_HEARTBEAT_FAILED = 10031

    # send_bet + ack
    TASK_SEND_BET_FAILED = 10040
    TASK_BET_MISMATCHED = 10041
    TASK_BET_AMOUNT_RULE_VIOLATED = 10042

    # 封包解析與例外
    TASK_PACKET_PARSE_FAILED = 10050
    TASK_DATA_INCOMPLETE = 10051
    TASK_EXCEPTION = 10099
    # 錢包加值任務
    TASK_RECHARGE_FAILED = 10060      # 轉帳 API 回傳失敗（success=False）
    TASK_RECHARGE_EXCEPTION = 10061   # 轉帳過程中發生例外（例如 POST 錯誤、response 解析錯誤）
    #餘額查詢任務
    TASK_RECHARGE_MISSING_KEY = 10062         # pf_id 或 api_key 遺失
    TASK_RECHARGE_INVALID_RESPONSE = 10063    # response 非 dict 結構
    TASK_RECHARGE_API_FAILED = 10064          # response.code != 0
    TASK_RECHARGE_MISSING_BALANCE = 10065     # response.data.balance 不存在

    # -------------------------------
    # ✅ 工具模組錯誤碼（40000～40999）
    # -------------------------------

    TOOL_FILE_NOT_FOUND = 40001
    TOOL_FILE_JSON_INVALID = 40002
    TOOL_FILE_LOAD_FAILED = 40003
    TOOL_FILE_EMPTY = 40004

    TOOL_REQUEST_GET_FAILED = 40010
    TOOL_REQUEST_POST_FAILED = 40011

    TOOL_ASSERT_STATUS_CODE_FAIL = 40020
    TOOL_ASSERT_KEY_MISSING = 40021
    TOOL_ASSERT_DATA_NOT_LIST = 40022
    TOOL_ASSERT_LIST_EMPTY = 40023
    TOOL_ASSERT_VALUE_MISMATCH = 40024

    TOOL_RESPONSE_KEY_MISSING = 40040
    TOOL_INVALID_RESPONSE_FORMAT = 40041
    TOOL_MISSING_DATA_FIELD = 40042
    TOOL_MISSING_TOKEN_FIELD = 40043

    TOOL_TOKEN_NOT_FOUND = 40050
    TOOL_TOKEN_LOAD_FAILED = 40051
    TOOL_TOKEN_MISSING_FIELD = 40052
    TOOL_TOKEN_TIME_PARSE_FAILED = 40053
    TOOL_TOKEN_EXPIRED = 40054
    TOOL_TOKEN_SAVE_FAILED = 40055

    TOOL_UNEXPECTED_ERROR = 40099
    TOOL_WS_ERROR = 40060
    TOOL_WS_CREATE_FAILED = 40061
    TOOL_WS_RUN_FAILED = 40062

    # -------------------------------
    # ✅ 保留錯誤碼（特殊用途或未分類）
    # -------------------------------

    TASK_PARTIAL_FAILED = 10098
    INVALID_TASK = 18888
    UNKNOWN_ERROR = 99999


# ✅ 錯誤碼分類
SUCCESS_CODES = {ResultCode.SUCCESS}
TASK_ERROR_CODES = {
    ResultCode.TASK_OID_LIST_FOR_TYPE_NOT_FOUND,
    ResultCode.TASK_WS_CONNECTION_FAILED,
    ResultCode.TASK_WS_CONNECTION_LOST,
    ResultCode.TASK_CONNECT_WS_FAILED,
    ResultCode.TASK_CALLBACK_TIMEOUT,
    ResultCode.TASK_BET_INFO_INCOMPLETE,
    ResultCode.TASK_TOTAL_BET_CALCULATION_FAILED,
    ResultCode.TASK_JOIN_ROOM_SERVER_ERROR,
    ResultCode.TASK_BET_CONTEXT_MISSING,
    ResultCode.TASK_SEND_HEARTBEAT_FAILED,
    ResultCode.TASK_HEARTBEAT_FAILED,
    ResultCode.TASK_SEND_BET_FAILED,
    ResultCode.TASK_BET_MISMATCHED,
    ResultCode.TASK_BET_AMOUNT_RULE_VIOLATED,
    ResultCode.TASK_PACKET_PARSE_FAILED,
    ResultCode.TASK_DATA_INCOMPLETE,
    ResultCode.TASK_EXCEPTION,
    ResultCode.TASK_PARTIAL_FAILED,
    ResultCode.TASK_PACKET_PARSE_FAILED,
    ResultCode.TASK_RECHARGE_FAILED,
    ResultCode.TASK_RECHARGE_EXCEPTION,
    ResultCode.TASK_RECHARGE_MISSING_KEY,
    ResultCode.TASK_RECHARGE_INVALID_RESPONSE,
    ResultCode.TASK_RECHARGE_API_FAILED,
    ResultCode.TASK_RECHARGE_MISSING_BALANCE,


}
TOOL_ERROR_CODES = {
    ResultCode.TOOL_FILE_NOT_FOUND,
    ResultCode.TOOL_FILE_JSON_INVALID,
    ResultCode.TOOL_FILE_LOAD_FAILED,
    ResultCode.TOOL_FILE_EMPTY,
    ResultCode.TOOL_REQUEST_GET_FAILED,
    ResultCode.TOOL_REQUEST_POST_FAILED,
    ResultCode.TOOL_ASSERT_STATUS_CODE_FAIL,
    ResultCode.TOOL_ASSERT_KEY_MISSING,
    ResultCode.TOOL_ASSERT_DATA_NOT_LIST,
    ResultCode.TOOL_ASSERT_LIST_EMPTY,
    ResultCode.TOOL_ASSERT_VALUE_MISMATCH,
    ResultCode.TOOL_RESPONSE_KEY_MISSING,
    ResultCode.TOOL_INVALID_RESPONSE_FORMAT,
    ResultCode.TOOL_WS_ERROR,
    ResultCode.TOOL_WS_CREATE_FAILED,
    ResultCode.TOOL_WS_RUN_FAILED,


}

GENERIC_ERROR_CODES = {
    ResultCode.INVALID_TASK,
    ResultCode.UNKNOWN_ERROR,
}


# ✅ 錯誤碼訊息定義
ERROR_MESSAGES = {
    ResultCode.SUCCESS: "任務成功",
    ResultCode.TASK_OID_LIST_FOR_TYPE_NOT_FOUND: "指定類型的 OID 清單不存在",
    ResultCode.TOOL_WS_ERROR: "WebSocket 發生異常",
    ResultCode.TOOL_WS_CREATE_FAILED: "WebSocket 建立失敗",
    ResultCode.TOOL_WS_RUN_FAILED: "WebSocket 執行緒啟動失敗",
    ResultCode.TASK_PACKET_PARSE_FAILED: "封包解析失敗",
    ResultCode.TASK_BET_MISMATCHED:"下注金額與線紅不符",
    ResultCode.TASK_RECHARGE_FAILED: "錢包加值失敗（伺服器回應非成功）",
    ResultCode.TASK_RECHARGE_EXCEPTION: "錢包加值過程發生例外",
    ResultCode.TASK_RECHARGE_MISSING_KEY: "查餘額缺少 pf_id 或 api_key",
    ResultCode.TASK_RECHARGE_INVALID_RESPONSE: "查餘額 API 回傳格式錯誤",
    ResultCode.TASK_RECHARGE_API_FAILED: "查餘額 API 回傳失敗",
    ResultCode.TASK_RECHARGE_MISSING_BALANCE: "查餘額結果缺少 balance 欄位",


    
    # 可視需求持續補上其他錯誤碼訊息
    ResultCode.INVALID_TASK: "無效任務",
    ResultCode.UNKNOWN_ERROR: "未知錯誤",
}