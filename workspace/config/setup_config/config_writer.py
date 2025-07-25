from pathlib import Path
from dotenv import dotenv_values
from workspace.tools.common.result_code import ResultCode

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_USER_PATH = ROOT_DIR / ".env.user"


def save_env_config(data: dict) -> int:
    try:
        existing = dotenv_values(ENV_USER_PATH) if ENV_USER_PATH.exists() else {}
        existing.update(data)
        content = "\n".join([f'{k}="{v}"' for k, v in existing.items()]) + "\n"
        ENV_USER_PATH.write_text(content, encoding="utf-8")
        return ResultCode.SUCCESS
    except Exception:
        return ResultCode.TASK_ENV_WRITE_FAILED
