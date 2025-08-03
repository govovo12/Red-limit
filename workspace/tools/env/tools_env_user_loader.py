from dotenv import dotenv_values
from workspace.config.paths import get_user_env_path

def load_user_config() -> dict:
    env_user_path = get_user_env_path()
    if not env_user_path.exists():
        return {}
    return dotenv_values(env_user_path)
