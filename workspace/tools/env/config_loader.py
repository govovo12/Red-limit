import os
from dotenv import dotenv_values
from workspace.config.paths import ROOT_DIR
from workspace.config.paths import get_env_path, get_user_env_path

def load_env(path_str: str) -> dict:
    full_path = ROOT_DIR / path_str
    print(f"[🔍] 嘗試讀取 {path_str} → {full_path}")
    if not full_path.exists():
        print(f"[⚠️] 檔案不存在：{path_str}")
        return {}
    return dotenv_values(full_path)

# ✅ 先載入兩份
env_default = dotenv_values(get_env_path())
env_user = dotenv_values(get_user_env_path())

# ✅ 合併邏輯（user 只有在有值時才覆蓋）
merged_env = {}
for key in set(env_default) | set(env_user):  # 所有 key 的 union
    user_val = env_user.get(key)
    default_val = env_default.get(key)
    merged_env[key] = user_val if user_val not in [None, ""] else default_val

# ✅ 寫入 os.environ
print("🧪 載入變數到 os.environ:")
for key, value in merged_env.items():
    if value is not None:
        print(f"  {key} = {value}")
        os.environ[key] = value
    else:
        print(f"  ⚠️ {key} 為 None，未設定")

# ✅ 安全取得函式
def safe_getenv(key, default=None, lower=False, rstrip_slash=False):
    val = os.getenv(key, default)
    if val is None:
        return default
    if lower:
        val = val.lower()
    if rstrip_slash:
        val = val.rstrip("/")
    return val

# ✅ 以下邏輯保留不變（完整照你原始邏輯）...
# 🔐 登入資訊
ADMIN_ACCOUNT = os.getenv("ADMIN_ACCOUNT")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
OTP_SECRET = os.getenv("OTP_SECRET")

# CMS
CMS_API_BASE_URL = os.getenv("CMS_API_BASE_URL")
CMS_LOGIN_PATH = os.getenv("CMS_LOGIN_PATH")
OID_PATH = os.getenv("OID_PATH")

# Headers
USER_AGENT = os.getenv("USER_AGENT")
ORIGIN = os.getenv("ORIGIN")
REFERER = os.getenv("REFERER")

# R88
PF_ID = os.getenv("PF_ID")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
BET_AMOUNT_RULE = os.getenv("BET_AMOUNT_RULE", "<=999999")
BET_LEVEL_MODE = safe_getenv("BET_LEVEL_MODE", "min", lower=True)

R88_API_BASE_URL = safe_getenv("R88_API_BASE_URL", "", rstrip_slash=True)
R88_TRANSFER_IN_PATH = os.getenv("R88_TRANSFER_IN_PATH", "")
R88_BALANCE_PATH = os.getenv("R88_BALANCE_PATH", "")
R88_TRANSFER_IN_URL = f"{R88_API_BASE_URL}{R88_TRANSFER_IN_PATH}"

R88_UNLOCK_WALLET_PATH = os.getenv("R88_UNLOCK_WALLET_PATH", "")
R88_UNLOCK_WALLET_URL = f"{R88_API_BASE_URL}{R88_UNLOCK_WALLET_PATH}"

R88_CHECK_ACCOUNT_PATH = os.getenv("R88_CHECK_ACCOUNT_PATH", "")
R88_CHECK_ACCOUNT_URL = f"{R88_API_BASE_URL}{R88_CHECK_ACCOUNT_PATH}"

# ✅ 補上這三行
R88_LOBBY_LOGIN_PATH = os.getenv("R88_LOBBY_LOGIN_PATH")
R88_ACCOUNT_LOGIN_PATH = os.getenv("R88_ACCOUNT_LOGIN_PATH")
R88_GAME_LIST_PATH = os.getenv("R88_GAME_LIST_PATH")

def get_check_account_url(account: str) -> str:
    return f"{R88_CHECK_ACCOUNT_URL.rstrip('/')}/{account}"

R88_GAME_WS_ORIGIN = os.getenv("R88_GAME_WS_ORIGIN")

TASK_LIST_MODE = os.getenv("task_list", "all")
CONCURRENCY_MODE = os.getenv("count", "all")

def get_ws_base_url_by_type_key(type_key: str) -> str:
    host = "ws://privatebeta-engine.r88-gaming.com"
    try:
        type_number = int(type_key.split("_")[1])
        port = 8080 + type_number
    except (IndexError, ValueError):
        port = 8082
    return f"{host}:{port}/ws/game"

DEBUG_WS_PACKET = safe_getenv("DEBUG_WS_PACKET", "false", lower=True) == "true"
DEBUG_WS_FALLBACK = safe_getenv("DEBUG_WS_FALLBACK", "false", lower=True) == "true"
LOG_PRINT_OUTPUT = safe_getenv("LOG_PRINT_OUTPUT", "true", lower=True) == "true"
