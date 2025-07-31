import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QStackedWidget

# ✅ 設定 PYTHONPATH 讓 workspace 可 import
sys.path.append(str(Path(__file__).resolve().parents[3]))

from workspace.gui.setup_config_gui_qt.ui_initializer import create_page1
from workspace.gui.setup_config_gui_qt.page2_ui import create_test_page as create_page2



class SetupWizard(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("設定與測試精靈")
        self.setFixedSize(600, 500)

        # Page 1：設定頁面（設定帳號、金鑰、限紅）
        page1 = create_page1(self)
        self.addWidget(page1)

        # Page 2：測試頁面（顯示目前設定、選擇 type、執行測試）
        page2 = create_page2(self)
        self.addWidget(page2)

        self.setCurrentIndex(0)  # 預設顯示 Page 1


def main():
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    wizard.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
