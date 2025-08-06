# workspace/config/paths.py

import sys
from pathlib import Path

def is_frozen() -> bool:
    return getattr(sys, "frozen", False)

def get_root_dir() -> Path:
    """
    可寫入資料夾（log / cache 等）
    - 打包：RedLimit.exe 所在資料夾
    - 本地：專案根目錄
    """
    if is_frozen():
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parents[2]

def get_resource_dir() -> Path:
    """
    唯讀資源位置（.env / assets）
    - 打包：PyInstaller 解壓的 _MEIPASS
    - 本地：專案根目錄
    """
    if is_frozen():
        return Path(sys._MEIPASS)
    else:
        return get_root_dir()

ROOT_DIR = get_root_dir()
RESOURCE_DIR = get_resource_dir()

# ✅ 可寫目錄
CACHE_DIR = ROOT_DIR / ".cache"
LOGS_DIR = ROOT_DIR / "logs"

# ✅ 唯讀資源目錄
ASSETS_DIR = RESOURCE_DIR / "workspace/assets"
ENV_PATH = RESOURCE_DIR / ".env"
USER_ENV_PATH = RESOURCE_DIR / ".env.user"

# ✅ 可寫檔案
OID_BY_TYPE_PATH = CACHE_DIR / "oid_by_type.json"
API_KEY_PATH = CACHE_DIR / "api_key.json"
REPORT_PATH = LOGS_DIR / "report.html"

# === 快取存取函式 ===
def get_env_path() -> Path:
    return ENV_PATH

def get_user_env_path() -> Path:
    return USER_ENV_PATH

def get_assets_dir() -> Path:
    return ASSETS_DIR

def get_oid_by_type_path() -> Path:
    return OID_BY_TYPE_PATH

def get_api_key_path() -> Path:
    return API_KEY_PATH

def get_oid_list_path() -> Path:
    return OID_BY_TYPE_PATH

def get_r88_api_key_path() -> Path:
    return CACHE_DIR / "r88_api_key.json"

def get_auth_token_cache_path() -> Path:
    return CACHE_DIR / "auth_token.json"

def get_token_lobby_cache_path() -> Path:
    return CACHE_DIR / "token_lobby.json"

def get_token_login_cache_path() -> Path:
    return CACHE_DIR / "token_login.json"

def get_token_lobby_cache_file(account: str) -> Path:
    return CACHE_DIR / f"token_lobby_{account}.json"

def get_token_login_cache_file(account: str) -> Path:
    return CACHE_DIR / f"token_login_{account}.json"

def get_last_test_log_path() -> Path:
    return CACHE_DIR / "last_test.log"

def get_log_report_path() -> Path:
    return REPORT_PATH

# === 自動建立資料夾（保險） ===
def ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def ensure_logs_dir():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
