@echo off

:: 切到 bat 所在資料夾
cd /d "%~dp0"
cd ..

echo 🛠️ 目前位置：%cd%

echo ✅ 啟用虛擬環境...
call venv\Scripts\activate

echo 🚀 開始打包 RedLimit.exe...
pyinstaller RedLimit.spec --noconfirm

echo ✅ 打包完成！請執行：
echo dist\RedLimit\RedLimit.exe

pause