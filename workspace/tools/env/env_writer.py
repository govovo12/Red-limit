from dotenv import dotenv_values
from workspace.tools.common.result_code import ResultCode
from workspace.config.paths import get_user_env_path
ENV_USER_PATH = get_user_env_path()

def save_env_config(data: dict) -> int:
    try:
        existing = dotenv_values(ENV_USER_PATH) if ENV_USER_PATH.exists() else {}
        existing.update(data)
        content = "\n".join([f'{k}="{v}"' for k, v in existing.items()]) + "\n"
        ENV_USER_PATH.write_text(content, encoding="utf-8")
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_ENV_WRITE_FAILED

def update_env(key: str, value: str) -> None:
    existing = dotenv_values(ENV_USER_PATH) if ENV_USER_PATH.exists() else {}
    existing[key] = value
    content = "\n".join([f"{k}={v}" for k, v in existing.items()]) + "\n"
    ENV_USER_PATH.write_text(content, encoding="utf-8")
