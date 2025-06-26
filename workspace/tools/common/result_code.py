# ✅ 錯誤碼定義模組
# ✅ 通用約定：
#   0 為成功
#   4xxxx 為工具模組層級錯誤碼（可被 retry / 捕捉）
#   後續可擴充 1xxxx 控制器、2xxxx combiner、3xxxx 任務模組

class ResultCode:
    # ✅ 通用成功
    SUCCESS = 0

    # -------------------------------
    # ✅ 工具模組錯誤（範圍：40000~49999）
    # -------------------------------

    # file_helper.py / data_loader.py
    TOOL_FILE_NOT_FOUND = 40001       # 檔案不存在
    TOOL_FILE_JSON_INVALID = 40002    # JSON 格式錯誤
    TOOL_FILE_LOAD_FAILED = 40003     # 未知檔案讀取錯誤
    TOOL_FILE_EMPTY = 40004           # 檔案為空

    # request_handler.py
    TOOL_REQUEST_GET_FAILED = 40010   # GET 請求失敗
    TOOL_REQUEST_POST_FAILED = 40011  # POST 請求失敗

    # assert_helper.py
    TOOL_ASSERT_STATUS_CODE_FAIL = 40020   # Status code 驗證失敗
    TOOL_ASSERT_KEY_MISSING = 40021        # 必要欄位缺失
    TOOL_ASSERT_DATA_NOT_LIST = 40022      # 回傳資料不是 list
    TOOL_ASSERT_LIST_EMPTY = 40023         # list 為空
    TOOL_ASSERT_VALUE_MISMATCH = 40024     # 數值比對不一致

    # otp_helper.py（預留）
    TOOL_OTP_GENERATE_FAIL = 40030         # OTP 產生失敗

    # log_helper.py / printer.py 不需回傳錯誤碼（純輸出）

    # response_helper.py
    TOOL_RESPONSE_KEY_MISSING     = 40040  # response 缺少 code / error_code 欄位
    TOOL_INVALID_RESPONSE_FORMAT  = 40041  # response 非 dict 格式
    TOOL_MISSING_DATA_FIELD       = 40042  # response 缺少 data 欄位
    TOOL_MISSING_TOKEN_FIELD      = 40043  # data 缺少 jwt / token / access_token
    TOOL_UNEXPECTED_ERROR = 40099

    # token_cache.py
    TOOL_TOKEN_NOT_FOUND = 40050
    TOOL_TOKEN_LOAD_FAILED = 40051
    TOOL_TOKEN_MISSING_FIELD = 40052
    TOOL_TOKEN_TIME_PARSE_FAILED = 40053
    TOOL_TOKEN_EXPIRED = 40054
    TOOL_TOKEN_SAVE_FAILED = 40055

    # -------------------------------
    # ✅ 任務模組錯誤（範圍：10000~19999）
    # -------------------------------

    TASK_OID_MIN_BET_INVALID = 16001  # 發現 min_bet 小於驗證門檻的 OID 房間
    TASK_GET_LOBBY_TOKEN_FAILED = 10002  # 獲取大廳 token 

    
    
    TASK_LOGIN_TO_ACCOUNT_FAILED=10004   #獲取帳號token
    TASK_PACKET_PARSE_FAILED = 10005  # 封包格式正確但結構錯誤（如缺少 data 欄位）

    # WebSocket 任務錯誤碼（10010～）
    TASK_WS_CONNECTION_FAILED = 10001       # 無法建立 WebSocket 連線
    TASK_WS_CONNECTION_LOST = 10002         # 建立後連線中斷
    TASK_CALLBACK_TIMEOUT = 10003

    # ws 錯誤（connect_to_game_ws 專用）
    TASK_CONNECT_WS_FAILED = 10020
    TASK_INVALID_JSON_MESSAGE = 10021
    TASK_BET_INFO_INCOMPLETE = 10022
    TASK_TOTAL_BET_CALCULATION_FAILED = 10023
    TASK_BET_AMOUNT_RULE_VIOLATED = 10024
    TASK_HEARTBEAT_TIMEOUT=10025
    TASK_BET_CONTEXT_MISSING = 10033       # 找不到預期的下注上下文（ws.bet_context）
    TASK_BET_MISMATCHED = 10034            # 回傳的 bet 值與預期不符
    TASK_ASSERT_VALUE_MISMATCH=10035

    # ✅ OID 提取與分類任務錯誤碼（新版 get_valid_oid_list_from_response 專用）
    TASK_EMPTY_GAME_LIST = 10040       # 找不到遊戲列表（data.game_option_list）
    TASK_EMPTY_OID_LIST = 10041        # 所有類型皆無有效 OID 資料
    # OID 類型快取解析錯誤（prepare_oid_list_by_type 任務模組專用）
    TASK_OID_CACHE_FORMAT_INVALID = 10050
    TASK_OID_LIST_FOR_TYPE_NOT_FOUND = 10051
    TASK_OID_CACHE_PARSE_FAILED = 10052
    
    TASK_EXCEPTION = 10099  # 任務模組內部發生未預期例外

    # open_single_ws_connection 任務錯誤碼
    TASK_SINGLE_WS_TOKEN_NOT_FOUND = 10030     # 找不到 login token 快取
    TASK_SINGLE_WS_OID_LIST_EMPTY = 10031      # OID 列表為空
    TASK_VALIDATE_OID_LIST_FORMAT_ERROR = 10032  # OID list 不是 int 陣列

    # -------------------------------
    # ✅ 系統級未知錯誤保底
    # -------------------------------
    UNKNOWN_ERROR = 99999
