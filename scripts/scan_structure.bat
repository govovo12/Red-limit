@echo off
REM ✅ 強制切回專案根目錄 Red-limit/
pushd "%~dp0\.."

REM ✅ 啟動 venv
call venv\Scripts\activate

REM ✅ 執行任務
python main.py --task scan_structure --type dummy

popd
pause
