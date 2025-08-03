from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]  # 根目錄（紅線往上兩層）
ENV_PATH = ROOT_DIR / ".env"  # env檔的位置

# log 輸出資料夾統一定義在這
LOBBY_LOG_DIR = Path(".log/lobby")
LOBBY_LOG_DIR.mkdir(parents=True, exist_ok=True)

# 各種 log 檔路徑
MIN_BET_LOG_PATH = LOBBY_LOG_DIR / "min_bet_all.log"
MIN_BET_VIOLATION_LOG_PATH = LOBBY_LOG_DIR / "min_bet_violation.log"



OID_BY_TYPE_PATH = Path(".cache/oid_by_type.json")

def get_oid_by_type_path() -> Path:
    return OID_BY_TYPE_PATH

def get_api_key_path() -> Path:
    return ROOT_DIR / ".cache" / "api_key.json"

def get_oid_list_path() -> Path:
    return Path(".cache/oid_by_type.json")

# 👉 .env.user 檔案路徑（專給 GUI 工具使用）
def get_user_env_path() -> Path:
    return ROOT_DIR / ".env.user"

