# workspace/init_env.py
def setup():
    """
    初始化專案執行環境：
    - 在 PyInstaller 模式下正確設置 workspace 為 import module path
    - 載入根目錄下的 .env 環境變數
    """
    import sys
    from pathlib import Path
    from dotenv import load_dotenv

    # 判斷是否為 PyInstaller 打包模式
    if getattr(sys, 'frozen', False):
        # 單檔執行模式
        root_path = Path(sys._MEIPASS)  # 解壓後的虛擬目錄
    else:
        # 原始碼模式
        root_path = Path(__file__).resolve().parents[1]

    # workspace 實體目錄
    workspace_path = root_path / "workspace"
    if str(workspace_path) not in sys.path:
        sys.path.insert(0, str(workspace_path))

    # 載入 .env（如果存在）
    env_path = root_path / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
