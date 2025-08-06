# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_dir = Path(".").resolve()
block_cipher = None

a = Analysis(
    [str(project_dir / "main.py")],  # ✅ 指定你真正的主程式
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        # ✅ 環境設定檔（打包到 dist/RedLimit 根目錄）
        (str(project_dir / ".env"), "."),
        (str(project_dir / ".env.user"), "."),

        # ✅ 靜態資源與程式碼
        (str(project_dir / "workspace/assets"), "workspace/assets"),
        (str(project_dir / "workspace"), "workspace"),
    ],
    hiddenimports=[
        *collect_submodules("workspace"),  # ✅ 全部 workspace 模組自動包含
        "requests",
        "dotenv",
        "PyQt5",
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
        "PyQt5.QtSvg",
        "PyQt5.sip",
        "sip",  # ✅ 消除 sip 警告
        "websockets",
        "httpx",
        "aiohttp",
        "ujson",
        "orjson",
        "rich",
        "customtkinter",
        "zdata",  # ✅ 消除找不到 zdata 警告（即使你沒用也加）
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RedLimit",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_dir / "IconGroup1.ico"),  # ✅ icon 絕對路徑（或使用 Path 拼）
)


coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="RedLimit"
)
