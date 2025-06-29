# ✅ 錯誤碼定義模組
# ✅ 通用約定：
#   0 為成功
#   4xxxx 為工具模組層級錯誤碼（可被 retry / 捕捉）
#   1xxxx 控制器錯誤、2xxxx combiner、3xxxx 預留
#   100xx 為 WebSocket 任務錯誤

class ResultCode:
    # ✅ 通用成功
    SUCCESS = 0

    # -------------------------------
    # ✅ 工具模組錯誤碼（40000～40999）
    # -------------------------------

    # file_helper.py / data_loader.py
    TOOL_FILE_NOT_FOUND = 40001
    TOOL_FILE_JSON_INVALID = 40002
    TOOL_FILE_LOAD_FAILED = 40003
    TOOL_FILE_EMPTY = 40004

    # request_handler.py
    TOOL_REQUEST_GET_FAILED = 40010
    TOOL_REQUEST_POST_FAILED = 40011

    # assert_helper.py
    TOOL_ASSERT_STATUS_CODE_FAIL = 40020
    TOOL_ASSERT_KEY_MISSING = 40021
    TOOL_ASSERT_DATA_NOT_LIST = 40022
    TOOL_ASSERT_LIST_EMPTY = 40023
    TOOL_ASSERT_VALUE_MISMATCH = 40024

    # otp_helper.py（預留）
    TOOL_OTP_GENERATE_FAIL = 40030

    # response_helper.py
    TOOL_RESPONSE_KEY_MISSING = 40040
    TOOL_INVALID_RESPONSE_FORMAT = 40041
    TOOL_MISSING_DATA_FIELD = 40042
    TOOL_MISSING_TOKEN_FIELD = 40043

    TOOL_UNEXPECTED_ERROR = 40099

    # token_cache.py
    TOOL_TOKEN_NOT_FOUND = 40050
    TOOL_TOKEN_LOAD_FAILED = 40051
    TOOL_TOKEN_MISSING_FIELD = 40052
    TOOL_TOKEN_TIME_PARSE_FAILED = 40053
    TOOL_TOKEN_EXPIRED = 40054
    TOOL_TOKEN_SAVE_FAILED = 40055

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

    # -------------------------------
    # ✅ 任務模組保留區 / 非 WebSocket（保留原始定義）
    # -------------------------------

    TASK_GET_LOBBY_TOKEN_FAILED = 10002
    TASK_LOGIN_TO_ACCOUNT_FAILED = 10004
    TASK_SINGLE_WS_TOKEN_NOT_FOUND = 10030
    TASK_SINGLE_WS_OID_LIST_EMPTY = 10031
    TASK_VALIDATE_OID_LIST_FORMAT_ERROR = 10032
    TASK_EMPTY_GAME_LIST = 10040
    TASK_EMPTY_OID_LIST = 10041
    TASK_OID_CACHE_FORMAT_INVALID = 10050
    TASK_OID_LIST_FOR_TYPE_NOT_FOUND = 10051
    TASK_OID_CACHE_PARSE_FAILED = 10052

    # join_room retry 錯誤
    TASK_JOIN_ROOM_SERVER_ERROR = 10102

    # 任務階段性失敗
    TASK_PARTIAL_FAILED = 10098
    TASK_TIMEOUT = 10099

    # -------------------------------
    # ✅ 保留錯誤碼（目前未動但用途特殊）
    # -------------------------------
    TASK_OID_MIN_BET_INVALID = 16001  # ⚠️ 目前保留，不動
    INVALID_TASK = 18888              # ⚠️ 保留給主控驗證任務型別

    # -------------------------------
    # ✅ 系統級未知錯誤保底
    # -------------------------------
    UNKNOWN_ERROR = 99999
