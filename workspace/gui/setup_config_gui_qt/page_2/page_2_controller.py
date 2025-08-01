from workspace.gui.setup_config_gui_qt.page_2.page_2_ui import create_page2_ui
from workspace.gui.setup_config_gui_qt.page_2.page_2_ux import setup_page2_logic

def register_page2(stack_widget):
    """
    建立 Page2 的 UI，綁定 UX 邏輯，並加入 stack_widget。
    """
    page1_widgets = create_page2_ui(stack_widget)
    setup_page2_logic(page1_widgets, stack_widget)
    stack_widget.addWidget(page1_widgets["page"])
