@echo off
chcp 65001 > nul

:: 切到 bat 所在位置的上層
cd /d "%~dp0"
cd ..

echo 🛠️ 目前位置：%cd%

echo ✅ 啟動虛擬環境...
call venv\Scripts\activate

echo 🔥 刪除 build 資料夾...
rmdir /s /q build

echo 🔥 刪除 dist 資料夾...
rmdir /s /q dist

echo 🚀 開始打包 Onefile RedLimit.exe...
pyinstaller RedLimit.spec

echo ✅ 打包完成！請執行：
echo dist\RedLimit.exe

pause
