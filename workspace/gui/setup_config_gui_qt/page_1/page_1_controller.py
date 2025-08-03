from PyQt5.QtWidgets import QPushButton, QVBoxLayout

from workspace.gui.setup_config_gui_qt.page_1.page_1_ui import build_page_1_ui
from workspace.gui.setup_config_gui_qt.page_1.page_1_ux import (
    get_intro_card,
    get_page2_help_card,
    get_page3_help_card,
)


def register_page1(stack_widget, switch_to_page_callback=None):
    """
    建立 Page1 的畫面，插入 UX 卡片元件至 UI slot 中，並加入堆疊。
    """
    ui = build_page_1_ui()

    # 🎯 插入 UX 說明卡片
    ui["slots"]["intro"].addWidget(get_intro_card())
    ui["slots"]["page2_help"].addWidget(get_page2_help_card())
    ui["slots"]["page3_help"].addWidget(get_page3_help_card())

    # 🚀 可選：加入跳轉 Page2 按鈕（建議放在 page3_help 區塊下方）
    if switch_to_page_callback:
        jump_btn = QPushButton("➡️ 前往參數設定（Page2）")
        jump_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 6px 12px;
                background-color: #2d7a38;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        layout: QVBoxLayout = ui["slots"]["page3_help"]
        layout.addWidget(jump_btn)
        jump_btn.clicked.connect(lambda: switch_to_page_callback(1))

    # ✅ 加入畫面
    stack_widget.addWidget(ui["widget"])
    return ui
