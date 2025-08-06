import sys
import os
from pathlib import Path

# ✅ 加入 PYTHONPATH，支援 workspace import（不依賴 paths.py 自身）
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from PyQt5.QtWidgets import QApplication, QStackedWidget

# ✅ 各子控制器
from workspace.gui.setup_config_gui_qt.page_1.page_1_controller import register_page1
from workspace.gui.setup_config_gui_qt.page_2.page_2_controller import register_page2
from workspace.gui.setup_config_gui_qt.page_3.page_3_controller import create_page_3



class SetupWizard(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("限紅測試平台")
        self.resize(960, 720)

        # Page1 是 index 0
        register_page1(self, self.setCurrentIndex)

        # ✅ 先建立 Page3，但不要馬上加
        page3_widget, go_to_page3 = create_page_3(self)

        # ✅ 接著加 Page2（會成為 index 1）
        register_page2(self, go_to_page3)

        # ✅ 最後加 Page3（會是 index 2）
        self.addWidget(page3_widget)


def main():
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    wizard.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
