@echo off
REM 🔍 掃描所有 .py 檔案是否含有硬寫路徑（不是透過 paths 取得的）

REM 切換到 Red-limit 專案根目錄
cd /d "%~dp0\.."

REM 印出目前目錄（debug用）
echo 📂 現在位置是：
cd

REM 啟動虛擬環境
call venv\Scripts\activate

REM 執行任務
python main.py --task scan_path_hardcode --type dummy

pause
