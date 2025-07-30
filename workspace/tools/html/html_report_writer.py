from pathlib import Path
from typing import List
from workspace.config.paths import ROOT_DIR


def write_html_report(type_key: str, lines: List[str]) -> None:
    report_path = ROOT_DIR / "logs" / f"{type_key}_report.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # ✅ 修正：若是單一長字串，先拆成多行
    if len(lines) == 1 and "\n" in lines[0]:
        lines = lines[0].splitlines()

    raw_block = "<br>".join(lines)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>{type_key} 測試報告</title>
    </head>
    <body>
        <h2>{type_key} 測試報告 - DEBUG 原始資料</h2>
        <div style=\"font-family:monospace;white-space:pre-wrap;\">{raw_block}</div>
    </body>
    </html>
    """

    try:
        print(f"📝 準備寫入報表：{report_path}")
        report_path.write_text(html, encoding="utf-8")
    except Exception as e:
        print(f"❌ 寫入失敗：{e}")


def write_index_html(type_keys: List[str]) -> None:
    index_path = ROOT_DIR / "logs" / "index.html"
    links = "\n".join([f"<li><a href='{t}_report.html'>{t} 測試報告</a></li>" for t in type_keys])

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>測試報告總覽</title>
    </head>
    <body>
        <h1>測試報告總覽</h1>
        <ul>
            {links}
        </ul>
    </body>
    </html>
    """

    try:
        index_path.write_text(html, encoding="utf-8")
    except Exception as e:
        print(f"❌ index.html 寫入失敗：{e}")
