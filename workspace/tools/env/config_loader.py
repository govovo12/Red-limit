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

# ws連線

R88_GAME_WS_BASE_URL = os.getenv("R88_GAME_WS_BASE_URL")
R88_GAME_WS_ORIGIN = os.getenv("R88_GAME_WS_ORIGIN")


BET_AMOUNT_RULE = os.getenv("BET_AMOUNT_RULE", "<=999999")
BET_LEVEL_MODE = os.getenv("BET_LEVEL_MODE", "min").lower()


