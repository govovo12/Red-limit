from workspace.config.paths import get_log_report_path
import webbrowser
from PyQt5.QtWidgets import QMessageBox

def open_report():
    path = get_log_report_path()
    if not path.exists():
        QMessageBox.warning(None, "錯誤", f"❌ 找不到報告：\n{path}")
        return
    webbrowser.open(str(path.resolve()))
