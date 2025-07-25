@echo off
cd /d %~dp0
cd ..

:: 強制使用正確的 python 路徑
set PYTHON_PATH=venv\Scripts\python.exe
echo [DEBUG] 使用的 Python 路徑：%PYTHON_PATH%
%PYTHON_PATH% -c "import sys; print('[DEBUG] 正在使用 Python =', sys.executable)"

:: 執行子控制器
%PYTHON_PATH% -m workspace.config.setup_config.subcontrollers.setup_config_controller

pause
