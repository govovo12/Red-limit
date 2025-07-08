class ResultCode:
    # ✅ 成功碼定義
    SUCCESS = 0

# region 🔐 login 子控任務支線（10000 ~ 19999）

    # --- generate_r88_api_key.py
    TASK_API_KEY_GENERATION_FAILED = 10001
    TASK_API_KEY_CACHE_FAILED = 10002
    TASK_API_KEY_LOAD_FAILED = 10003

    # --- get_lobby_info.py
    TASK_LOBBY_API_REQUEST_FAILED = 10004
    TASK_LOBBY_URL_MISSING = 10005
    TASK_LOBBY_TOKEN_EXTRACTION_FAILED = 10006

    # login_to_r88_account.py
    TASK_LOBBY_TOKEN_NOT_FOUND = 10007
    TASK_ACCOUNT_LOGIN_API_FAILED = 10008
    TASK_ACCESS_TOKEN_MISSING = 10009

    # get_game_option_response.py
    TASK_LOGIN_TOKEN_NOT_FOUND = 10010
    TASK_GAME_LIST_API_FAILED = 10011

    # prepare_game_classification_input.py
    TASK_GAME_LIST_STRUCTURE_INVALID = 10012

    # count_oid_entries.py
    TASK_OID_MAP_INVALID = 10014

# region 🧩 batch 子控任務支線（20000 ~ 29999）

    # --- prepare_oid_list_by_type.py
    TASK_OID_LIST_FOR_TYPE_NOT_FOUND = 20001

    # --- generate_account_oid_pairs.py
    TASK_ACCOUNT_PAIRING_EMPTY_INPUT = 20002

    # --- login_task.py
    TASK_LOBBY_API_KEY_LOAD_FAILED = 20003
    TASK_LOBBY_TOKEN_EXTRACTION_FAILED = 20004
    TASK_GET_LOBBY_TOKEN_FAILED = 20005

    # --- get_access_token_task.py
    TASK_LOGIN_TO_ACCOUNT_FAILED = 20006




    # ✅ 工具錯誤碼定義（40000 ~ 49999）
    TOOL_FILE_NOT_FOUND = 40010
    TOOL_JSON_DECODE_FAILED = 40011
    TOOL_REQUEST_FAILED = 40030
    TOOL_TIMEOUT = 40031
    TOOL_WS_CONNECT_FAILED = 40050
    TOOL_WS_ALREADY_CONNECTED = 40051
    TOOL_ENV_VAR_MISSING = 40070
    TOOL_INVALID_RULE_FORMAT = 40071
    TOOL_UNSUPPORTED_OPERATION = 40090

    # ✅ 通用錯誤碼定義（50000+）
    TASK_EXCEPTION = 50001

    # ✅ 成功碼集合
    SUCCESS_CODES = {
        SUCCESS,
    }

    # ✅ 任務錯誤碼集合
    TASK_ERROR_CODES = {
        TASK_API_KEY_GENERATION_FAILED,
        TASK_API_KEY_CACHE_FAILED,

        TASK_API_KEY_LOAD_FAILED,
        TASK_LOBBY_API_REQUEST_FAILED,
        TASK_LOBBY_URL_MISSING,
        TASK_LOBBY_TOKEN_EXTRACTION_FAILED,

        TASK_LOBBY_TOKEN_NOT_FOUND,
        TASK_ACCOUNT_LOGIN_API_FAILED,
        TASK_ACCESS_TOKEN_MISSING,

        TASK_LOGIN_TOKEN_NOT_FOUND,
        TASK_GAME_LIST_API_FAILED,

        TASK_GAME_LIST_STRUCTURE_INVALID,

        TASK_OID_MAP_INVALID,

        TASK_OID_LIST_FOR_TYPE_NOT_FOUND,

        TASK_ACCOUNT_PAIRING_EMPTY_INPUT,

        TASK_LOBBY_API_KEY_LOAD_FAILED,
        TASK_LOBBY_TOKEN_EXTRACTION_FAILED,
        TASK_GET_LOBBY_TOKEN_FAILED,

        TASK_LOGIN_TO_ACCOUNT_FAILED,




    }

    # ✅ 工具錯誤碼集合
    TOOL_ERROR_CODES = {
        TOOL_FILE_NOT_FOUND,
        TOOL_JSON_DECODE_FAILED,
        TOOL_REQUEST_FAILED,
        TOOL_TIMEOUT,
        TOOL_WS_CONNECT_FAILED,
        TOOL_WS_ALREADY_CONNECTED,
        TOOL_ENV_VAR_MISSING,
        TOOL_INVALID_RULE_FORMAT,
        TOOL_UNSUPPORTED_OPERATION,
    }

    # ✅ 通用錯誤碼集合
    GENERIC_ERROR_CODES = {
        TASK_EXCEPTION,
    }

    # ✅ 錯誤訊息對照表
    ERROR_MESSAGES = {

        # 成功
        SUCCESS: "執行成功",

        # 工具錯誤
        TOOL_FILE_NOT_FOUND: "檔案未找到",
        TOOL_JSON_DECODE_FAILED: "JSON 解碼錯誤",
        TOOL_REQUEST_FAILED: "發送請求失敗",
        TOOL_TIMEOUT: "執行逾時",
        TOOL_WS_CONNECT_FAILED: "WebSocket 建立失敗",
        TOOL_WS_ALREADY_CONNECTED: "WebSocket 已連線",
        TOOL_ENV_VAR_MISSING: "環境變數缺失",
        TOOL_INVALID_RULE_FORMAT: "規則格式錯誤",
        TOOL_UNSUPPORTED_OPERATION: "不支援的操作",

        # 任務錯誤
        TASK_API_KEY_GENERATION_FAILED: "API Key 產生失敗",
        TASK_API_KEY_CACHE_FAILED: "API Key 快取寫入失敗",
        TASK_API_KEY_LOAD_FAILED: "API 金鑰載入失敗",
        TASK_LOBBY_API_REQUEST_FAILED: "大廳登入 API 請求失敗",
        TASK_LOBBY_URL_MISSING: "API 回傳缺少 URL",
        TASK_LOBBY_TOKEN_EXTRACTION_FAILED: "大廳 token 擷取失敗",
        TASK_LOBBY_TOKEN_NOT_FOUND: "找不到對應的大廳 token",
        TASK_ACCOUNT_LOGIN_API_FAILED: "帳號登入 API 請求失敗",
        TASK_ACCESS_TOKEN_MISSING: "API 回傳缺少 access_token",
        TASK_LOGIN_TOKEN_NOT_FOUND: "找不到登入 token",
        TASK_GAME_LIST_API_FAILED: "遊戲列表 API 請求失敗",
        TASK_GAME_LIST_STRUCTURE_INVALID: "遊戲列表結構異常，無法解析分類與資料",
        TASK_OID_MAP_INVALID: "OID map 結構錯誤或格式不符",
        TASK_OID_LIST_FOR_TYPE_NOT_FOUND: "無法取得指定類型的 OID 清單",
        TASK_ACCOUNT_PAIRING_EMPTY_INPUT: "OID 清單為空，無法配對帳號",
        TASK_LOBBY_API_KEY_LOAD_FAILED: "無法讀取大廳登入所需 API 金鑰",
        TASK_LOBBY_TOKEN_EXTRACTION_FAILED: "無法從 API 回傳中擷取 token",
        TASK_GET_LOBBY_TOKEN_FAILED: "登入過程發生未預期錯誤",
        TASK_LOGIN_TO_ACCOUNT_FAILED: "帳號登入失敗，無法取得 access_token",




        # 通用錯誤
        TASK_EXCEPTION: "未預期的任務錯誤",
    }
