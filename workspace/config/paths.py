# workspace/config/paths.py

import sys
from pathlib import Path

def get_env_path() -> Path:
    return ENV_PATH

def get_root_dir() -> Path:
    """
    回傳專案根目錄
    ✅ 支援 .py 開發模式
    ✅ 支援 PyInstaller 打包後的 .exe 模式
    """
    if getattr(sys, "frozen", False):
        # ✅ exe 模式：取 RedLimit.exe 所在資料夾
        return Path(sys.executable).parent
    else:
        # ✅ 開發模式：從 paths.py 推回專案根目錄
        return Path(__file__).resolve().parents[2]

ROOT_DIR = get_root_dir()
INTERNAL_ROOT = ROOT_DIR / "_internal" if getattr(sys, "frozen", False) else ROOT_DIR

# === 資料夾 ===
CACHE_DIR = ROOT_DIR / ".cache"
LOGS_DIR = ROOT_DIR / "logs"
ASSETS_DIR = ROOT_DIR / "workspace" / "assets"

# === 檔案 ===
ENV_PATH = ROOT_DIR / ( "_internal/.env" if getattr(sys, "frozen", False) else ".env" )
USER_ENV_PATH = ROOT_DIR / ( "_internal/.env.user" if getattr(sys, "frozen", False) else ".env.user" )
OID_BY_TYPE_PATH = CACHE_DIR / "oid_by_type.json"
API_KEY_PATH = CACHE_DIR / "api_key.json"
REPORT_PATH = LOGS_DIR / "report.html"

# === 快取路徑取得函式 ===
def get_oid_by_type_path() -> Path:
    return OID_BY_TYPE_PATH

def get_api_key_path() -> Path:
    return API_KEY_PATH

def get_oid_list_path() -> Path:
    return OID_BY_TYPE_PATH

def get_user_env_path() -> Path:
    return USER_ENV_PATH

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

def get_assets_dir() -> Path:
    return ASSETS_DIR

# === 可選：自動建立目錄保險用 ===
def ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def ensure_logs_dir():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
