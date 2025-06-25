@echo off
cd /d %~dp0

:: 啟動虛擬環境
call venv\Scripts\activate.bat

:: 設定 PYTHONPATH 為當前目錄
set PYTHONPATH=%cd%

:: 執行 pytest，傳入任何參數
pytest %*

pause
