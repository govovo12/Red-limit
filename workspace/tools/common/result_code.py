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

# tpye_2任務專用(30000-39999)
    # 🚀 open_ws_connection_task.py
    TASK_OPEN_WS_CONNECTION_FAILED = 30000

    # 🎯 handle_join_room_async.py 
    TASK_JOIN_ROOM_SERVER_ERROR = 30030
    TASK_JOIN_ROOM_EVENT_MISMATCH = 30031
    TASK_BET_INFO_INCOMPLETE = 30032
    TASK_PACKET_PARSE_FAILED = 30033

    # 💰 recharge_wallet_task.py 
    TASK_RECHARGE_FAILED = 30033
    TASK_RECHARGE_EXCEPTION = 30034

    # 💓 send_heartbeat_task.py
    TASK_SEND_HEARTBEAT_FAILED = 30035 

    # 🎯 send_bet_task.py
    TASK_BET_CONTEXT_MISSING = 30036
    TASK_SEND_BET_FAILED = 30037

    # 🎯 parse_bet_response.py
    TASK_BET_ACK_DATA_INCOMPLETE = 30038
    TASK_BET_MISMATCHED = 30039
    TASK_BET_AMOUNT_VIOLATED = 30040
    TASK_BET_ACK_PARSE_FAILED = 30041

    # 🔁 send_round_finished.py
    TASK_SEND_ROUND_FINISHED_FAILED = 30042
    

    # 🚪 send_exit_room.py
    TASK_SEND_EXIT_ROOM_FAILED = 30043




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

    # 🔌 ws_connection_async_helper.py 專用錯誤碼（40010 起）
    TOOL_WS_CONNECT_FAILED = 40010
    TOOL_WS_CLOSE_FAILED = 40011
    TOOL_WS_RECV_TIMEOUT = 40012
    TOOL_WS_RECV_LOOP_ERROR = 40013
    TOOL_WS_INVALID_JSON = 40014
    TOOL_WS_DISPATCH_FAILED = 40015

    #🔌ws_event_dispatcher_async.py
    TOOL_WS_DISPATCH_FAILED = 40016  
    TOOL_WS_EVENT_MISMATCH=40019
    # 🧰 ws_step_runner_async.py
    TOOL_WS_TIMEOUT = 40017
    TOOL_WS_INVALID_DATA = 40018
    TOOL_WS_CALLBACK_NOT_SET = 40019

    # ✅ 通用錯誤碼定義（50000+）
    TASK_EXCEPTION = 50001
    INVALID_TASK = 50002  # 50001 是 TASK_EXCEPTION
    TASK_PARTIAL_FAILED = 50003
    TASK_WS_TIMEOUT=50004

# region 🛡️ 通用型任務模組（60000 ~ 69999）
    # --- check_account_task.py
    TASK_ACCOUNT_NOT_LINKED = 60001
    TASK_API_KEY_MISSING = 60002
    TASK_CHECK_ACCOUNT_FAILED = 60003
    # --- unlock_wallet_task.py
    TASK_UNLOCK_WALLET_FAILED = 60004
    TASK_UNLOCK_WALLET_EXCEPTION = 60005
  
  
  
    # ✅ 成功碼集合
    SUCCESS_CODES = {
        SUCCESS,
    }

    # ✅ 任務錯誤碼集合
    TASK_ERROR_CODES = {

        TASK_ACCOUNT_NOT_LINKED ,
        TASK_API_KEY_MISSING ,
        TASK_CHECK_ACCOUNT_FAILED ,

        TASK_UNLOCK_WALLET_FAILED,
        TASK_UNLOCK_WALLET_EXCEPTION,

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

        TASK_OPEN_WS_CONNECTION_FAILED,

        TASK_JOIN_ROOM_SERVER_ERROR,
        TASK_JOIN_ROOM_EVENT_MISMATCH,
        TASK_BET_INFO_INCOMPLETE,
        TASK_PACKET_PARSE_FAILED,

        TASK_RECHARGE_FAILED,
        TASK_RECHARGE_EXCEPTION,

        TASK_SEND_HEARTBEAT_FAILED,

        TASK_BET_CONTEXT_MISSING,
        TASK_SEND_BET_FAILED,
        
        TASK_BET_ACK_DATA_INCOMPLETE,
        TASK_BET_MISMATCHED,
        TASK_BET_AMOUNT_VIOLATED,
        TASK_BET_ACK_PARSE_FAILED,
        TASK_SEND_ROUND_FINISHED_FAILED,

        TASK_SEND_EXIT_ROOM_FAILED,


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

        TOOL_WS_CONNECT_FAILED,
        TOOL_WS_CLOSE_FAILED,
        TOOL_WS_RECV_TIMEOUT,
        TOOL_WS_RECV_LOOP_ERROR,
        TOOL_WS_INVALID_JSON,
        TOOL_WS_DISPATCH_FAILED,
        TOOL_WS_DISPATCH_FAILED,

        TOOL_WS_TIMEOUT,
        TOOL_WS_INVALID_DATA,
        TOOL_WS_EVENT_MISMATCH,
        TOOL_WS_CALLBACK_NOT_SET,
    }

    # ✅ 通用錯誤碼集合
    GENERIC_ERROR_CODES = {
        TASK_EXCEPTION,
        INVALID_TASK,
        TASK_PARTIAL_FAILED,
        TASK_WS_TIMEOUT
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
        TOOL_WS_CONNECT_FAILED: "建立 WebSocket 連線失敗",
        TOOL_WS_CLOSE_FAILED: "關閉 WebSocket 連線失敗",
        TOOL_WS_RECV_TIMEOUT: "接收 WebSocket 訊息逾時",
        TOOL_WS_RECV_LOOP_ERROR: "接收 WebSocket 訊息時發生非預期錯誤",
        TOOL_WS_INVALID_JSON: "接收到無效的 JSON 格式資料",
        TOOL_WS_DISPATCH_FAILED: "事件分派處理失敗",
        TOOL_WS_DISPATCH_FAILED: "WebSocket 事件分派處理失敗",
        TOOL_WS_TIMEOUT: "等待 WebSocket 回應超時",
        TOOL_WS_INVALID_DATA: "收到不符合預期的 WebSocket 回應資料",
        TOOL_WS_EVENT_MISMATCH:"收到不符合預期的封包",
        TOOL_WS_CALLBACK_NOT_SET: "任務模組未設定錯誤碼，callback 結果無法判斷",


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
        TASK_OPEN_WS_CONNECTION_FAILED: "建立 WebSocket 連線時發生未預期例外",
        TASK_JOIN_ROOM_SERVER_ERROR: "伺服器回傳 server_error 封包",
        TASK_JOIN_ROOM_EVENT_MISMATCH: "非預期封包事件類型，應為 join_room",
        TASK_BET_INFO_INCOMPLETE: "下注資料 bet_info 缺失或格式錯誤",
        TASK_PACKET_PARSE_FAILED: "封包解析錯誤（join_room）",
        TASK_RECHARGE_FAILED: "錢包加值失敗（API 回傳錯誤碼）",
        TASK_RECHARGE_EXCEPTION: "錢包加值時發生例外錯誤",
        TASK_SEND_HEARTBEAT_FAILED: "發送 keep_alive 封包失敗",
        TASK_BET_CONTEXT_MISSING: "缺少 ws.bet_context，無法送出下注封包",
        TASK_SEND_BET_FAILED: "發送 bet 封包時發生例外錯誤",
        TASK_BET_ACK_DATA_INCOMPLETE: "下注回應資料不完整（缺少 expected 或 actual）",
        TASK_BET_MISMATCHED: "下注金額不一致（與原始 total_bet 不符）",
        TASK_BET_AMOUNT_VIOLATED: "下注金額不符合限紅規則",
        TASK_BET_ACK_PARSE_FAILED: "下注回應封包解析發生例外錯誤",
        TASK_SEND_ROUND_FINISHED_FAILED: "發送 cur_round_finished 封包失敗",
        TASK_SEND_EXIT_ROOM_FAILED: "發送 exit_room 封包失敗",
        TASK_ACCOUNT_NOT_LINKED: "帳號尚未建立與平台的對應關係",
        TASK_API_KEY_MISSING: "無法取得 API 金鑰資料",
        TASK_CHECK_ACCOUNT_FAILED: "查詢帳號對應關係時發生例外錯誤",
        TASK_UNLOCK_WALLET_FAILED: "解鎖錢包失敗（API 回傳錯誤碼）",
        TASK_UNLOCK_WALLET_EXCEPTION: "解鎖錢包時發生例外錯誤",







        # 通用錯誤
        TASK_EXCEPTION: "未預期的任務錯誤",
        TASK_PARTIAL_FAILED: "部分任務成功，部分失敗",
        INVALID_TASK: "任務參數不完整（缺少 account、oid 或 token）",
        TASK_WS_TIMEOUT:"WS連線超時"

    }
