@echo off
cd /d C:\Users\user\Desktop\Red-limit

REM 啟動虛擬環境（call 是必要的，否則後面命令不會在虛擬環境裡執行）
call venv\Scripts\activate.bat

REM 執行互動式 Python 工具
python git_push_tool.py

REM 等待使用者關閉畫面
pause
