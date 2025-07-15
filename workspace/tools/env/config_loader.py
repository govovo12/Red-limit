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

# 🔓 解鎖錢包 API
R88_UNLOCK_WALLET_PATH = os.getenv("R88_UNLOCK_WALLET_PATH")
R88_UNLOCK_WALLET_URL = f"{R88_API_BASE_URL.rstrip('/')}{R88_UNLOCK_WALLET_PATH}"



# === 檢查平台帳號跟遊戲帳號用 API ===
R88_CHECK_ACCOUNT_PATH = os.getenv("R88_CHECK_ACCOUNT_PATH")
R88_CHECK_ACCOUNT_URL = f"{R88_API_BASE_URL.rstrip('/')}{R88_CHECK_ACCOUNT_PATH}"
def get_check_account_url(account: str) -> str:
    return f"{R88_CHECK_ACCOUNT_URL.rstrip('/')}/{account}"

# ws連線
R88_GAME_WS_ORIGIN = os.getenv("R88_GAME_WS_ORIGIN")

BET_AMOUNT_RULE = os.getenv("BET_AMOUNT_RULE", "<=999999")
BET_LEVEL_MODE = os.getenv("BET_LEVEL_MODE", "min").lower()


# 🧪 任務流程控制參數（從 .env 載入）
TASK_LIST_MODE = os.getenv("task_list", "all")        # e.g. "all", "0", "23"
CONCURRENCY_MODE = os.getenv("count", "all")          # e.g. "all", "1", "4"

def get_ws_base_url_by_type_key(type_key: str) -> str:
    """
    根據類型字串（如 'type_3'）自動決定 WebSocket port，例如 8080 + type編號。
    若格式錯誤或無法解析數字，fallback 為 8082（對應 type_2）。
    """
    host = "ws://privatebeta-engine.r88-gaming.com"
    try:
        type_number = int(type_key.split("_")[1])
        port = 8080 + type_number
    except (IndexError, ValueError):
        port = 8082  # fallback 預設為 type_2 port

    return f"{host}:{port}/ws/game"
