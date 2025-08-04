@echo off
cd /d "%~dp0\.."

REM 啟動 venv
call venv\Scripts\activate

REM 執行 git 工具
python workspace\tools\git\git_push_tool.py

REM 保留畫面
pause
