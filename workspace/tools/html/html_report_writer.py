from pathlib import Path
from typing import List, Dict

HTML_TEMPLATE = """
<html>
<head>
    <meta charset="utf-8">
    <title>測試報表</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f8f8f8; padding: 20px; }}
        details {{ background: #fff; margin-bottom: 16px; border: 1px solid #ccc; border-radius: 6px; padding: 10px; }}
        summary {{ font-size: 18px; font-weight: bold; cursor: pointer; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
        th {{ background-color: #f0f0f0; }}
        .fail-row {{ background-color: #ffecec; }}
        .stat-box {{ margin-top: 20px; padding: 12px; background: #fff; border: 1px solid #aaa; border-radius: 6px; font-size: 16px; }}
    </style>
</head>
<body>
    <h2>限紅測試報告</h2>
    {sections}
    <details open>
        <summary>❗ 所有失敗紀錄（共 {fail_count} 筆）</summary>
        {fail_table}
    </details>
    <div class="stat-box">
        ✅ 成功：{success_count} 筆　❌ 失敗：{fail_count} 筆　成功率：{success_rate:.1f}%
    </div>
</body>
</html>
"""

# 🔁 請注意 key 名與你 assemble_stat 回傳一致（首字大寫）
COLUMN_TITLES = {
    "Game": "遊戲",
    "Account": "帳號",
    "Expect": "預期值",
    "Actual": "實際值",
    "Mark": "結果",
}

def is_passed(value) -> bool:
    if not isinstance(value, str):
        return False
    return "passed" in value.strip().lower()

def is_failed(value) -> bool:
    if not isinstance(value, str):
        return False
    return "failed" in value.strip().lower() or "❌" in value

def render_table(rows: List[Dict]) -> str:
    if not rows:
        return "<p>無資料</p>"
    headers = rows[0].keys()
    header_html = "".join(f"<th>{COLUMN_TITLES.get(key, key)}</th>" for key in headers)
    body_html = ""
    for row in rows:
        cls = " class=\"fail-row\"" if is_failed(row.get("Mark")) else ""
        cells = "".join(f"<td>{value}</td>" for value in row.values())
        body_html += f"<tr{cls}>{cells}</tr>"
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{body_html}</tbody></table>"

def write_combined_report(type_to_rows: Dict[str, List[Dict]]) -> None:
    all_rows = []
    sections_html = ""

    for type_key, rows in type_to_rows.items():
        all_rows.extend(rows)
        section = f"""
        <details>
            <summary>{type_key.upper()} 測試結果（共 {len(rows)} 筆）</summary>
            {render_table(rows)}
        </details>
        """
        sections_html += section

    success_rows = [r for r in all_rows if is_passed(r.get("Mark"))]
    fail_rows = [r for r in all_rows if is_failed(r.get("Mark"))]
    success_count = len(success_rows)
    fail_count = len(fail_rows)
    total = success_count + fail_count
    success_rate = (success_count / total * 100) if total else 0.0

    fail_table_html = render_table(fail_rows)
    html_content = HTML_TEMPLATE.format(
        sections=sections_html,
        fail_count=fail_count,
        fail_table=fail_table_html,
        success_count=success_count,
        success_rate=success_rate
    )

    output_path = Path(__file__).resolve().parents[3] / "logs" / "report.html"
    output_path.write_text(html_content, encoding="utf-8")
