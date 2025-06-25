# workspace/init_env.py
def setup():
    """
    初始化專案執行環境：
    - 將 workspace 加入 PYTHONPATH
    - 載入根目錄下的 .env 環境變數
    """
    import sys
    from pathlib import Path
    from dotenv import load_dotenv

    # 專案根目錄（假設 init_env.py 在 workspace 下）
    root_path = Path(__file__).resolve().parents[1]

    # 加入 workspace 目錄到 sys.path
    workspace_path = root_path / "workspace"
    sys.path.insert(0, str(workspace_path))

    # 載入根目錄的 .env
    env_path = root_path / ".env"
    load_dotenv(dotenv_path=env_path)
