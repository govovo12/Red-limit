import os
from dotenv import load_dotenv
from workspace.config.paths import ENV_PATH

# 載入 .env 檔案
load_dotenv(dotenv_path=ENV_PATH)

# 🔐 登入用資訊
ADMIN_ACCOUNT = os.getenv("ADMIN_ACCOUNT")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
OTP_SECRET = os.getenv("OTP_SECRET")

# 🌐 CMS API 設定
CMS_API_BASE_URL = os.getenv("CMS_API_BASE_URL")
CMS_LOGIN_PATH = os.getenv("CMS_LOGIN_PATH")
OID_PATH = os.getenv("OID_PATH")


# 🌍 HTTP Header 預設參數
USER_AGENT = os.getenv("USER_AGENT")
ORIGIN = os.getenv("ORIGIN")
REFERER = os.getenv("REFERER")

# 🔐 R88 API 驗證資訊
PF_ID = os.getenv("PF_ID")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# 🌐 R88 API 共用設定
R88_API_BASE_URL = os.getenv("R88_API_BASE_URL")
R88_LOBBY_LOGIN_PATH = os.getenv("R88_LOBBY_LOGIN_PATH")
R88_ACCOUNT_LOGIN_PATH = os.getenv("R88_ACCOUNT_LOGIN_PATH")
R88_GAME_LIST_PATH = os.getenv("R88_GAME_LIST_PATH")
R88_TRANSFER_IN_PATH = os.getenv("R88_TRANSFER_IN_PATH")
#餘額轉帳URL
R88_BALANCE_PATH = os.getenv("R88_BALANCE_PATH")
# 💰 組合轉帳錢包 URL
R88_TRANSFER_IN_URL = f"{R88_API_BASE_URL.rstrip('/')}{R88_TRANSFER_IN_PATH}"
# ws連線


R88_GAME_WS_ORIGIN = os.getenv("R88_GAME_WS_ORIGIN")


BET_AMOUNT_RULE = os.getenv("BET_AMOUNT_RULE", "<=999999")
BET_LEVEL_MODE = os.getenv("BET_LEVEL_MODE", "min").lower()


# 🧪 任務流程控制參數（從 .env 載入）
TASK_LIST_MODE = os.getenv("task_list", "all")        # e.g. "all", "0", "23"
CONCURRENCY_MODE = os.getenv("count", "all")          # e.g. "all", "1", "4"

def get_ws_base_url_by_game_type(game_option_list_type: int) -> str:
    """
    根據 game_option_list_type 回傳對應的 WebSocket base URL。
    例如 type 3 使用 port 8083，其餘使用預設 8082。
    """
    host = "ws://privatebeta-engine.r88-gaming.com"
    port = 8083 if game_option_list_type == 3 else 8082
    return f"{host}:{port}/ws/game"