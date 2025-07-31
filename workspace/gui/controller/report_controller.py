from pathlib import Path
import webbrowser
from PyQt5.QtWidgets import QMessageBox

def open_report():
    report_path = Path(__file__).resolve().parents[3] / "logs" / "report.html"
    if report_path.exists():
        webbrowser.open(str(report_path))
    else:
        QMessageBox.warning(None, "報表不存在", "尚未產生報表，請先執行測試。")
