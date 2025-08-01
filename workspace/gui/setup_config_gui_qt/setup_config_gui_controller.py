import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QStackedWidget

# ✅ 設定 PYTHONPATH 讓 workspace 可 import
sys.path.append(str(Path(__file__).resolve().parents[3]))

from workspace.gui.setup_config_gui_qt.page_2.page_2_controller import register_page2
from workspace.gui.setup_config_gui_qt.page_3.page_3_controller import create_page_3



class SetupWizard(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("限紅測試平台")
        self.resize(960, 720)

        # Page 2：設定頁面
        register_page2(self)  # ❗ 不用接回傳值也不用再 addWidget

        # Page 3：測試頁面（已改為 Page 3，使用三層 MVC）
        page3 = create_page_3(self)
        self.addWidget(page3)



def main():
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    wizard.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
