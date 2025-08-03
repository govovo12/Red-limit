from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QFrame, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt


def build_page_1_ui():
    # === 最外層背景（含 gradient） ===
    outer_wrapper = QGroupBox()
    outer_wrapper.setStyleSheet("""
        QGroupBox {
            background-color: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #a8e063,
                stop:1 #56ab2f
            );
            border: none;
        }
    """)
    outer_layout = QVBoxLayout(outer_wrapper)
    outer_layout.setContentsMargins(0, 0, 0, 0)

    # === 加入可捲動區塊（避免卡死） ===
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameStyle(QFrame.NoFrame)
    outer_layout.addWidget(scroll)

    # === 中央內容容器 ===
    central = QFrame()
    central.setStyleSheet("background-color: transparent;")
    scroll.setWidget(central)

    central_layout = QVBoxLayout(central)
    central_layout.setAlignment(Qt.AlignTop)
    central_layout.setContentsMargins(0, 5, 0, 10)

    # === 限寬容器 ===
    content_frame = QFrame()
    content_frame.setStyleSheet("background: transparent;")
    content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    content_frame_layout = QVBoxLayout(content_frame)
    content_frame_layout.setSpacing(16)
    content_frame_layout.setContentsMargins(0, 0, 0, 0)
    central_layout.addWidget(content_frame)

    # === 頁面主標題 + 副標題，使用中間容器包住確保置中 ===
    title_container = QFrame()
    title_layout = QVBoxLayout(title_container)
    title_layout.setAlignment(Qt.AlignHCenter)
    title_layout.setContentsMargins(0, 0, 0, 0)

    title = QLabel("限紅測試平台 - 使用說明")
    title.setStyleSheet("""
        font-size: 26px;
        font-weight: bold;
        color: #d32f2f;
        padding-bottom: 2px;
    """)
    subtitle = QLabel("自動化測試人員操作指南，說明流程與設定方式")
    subtitle.setStyleSheet("""
        font-size: 14px;
        color: #eeeeee;
        padding-bottom: 4px;
    """)

    title_layout.addWidget(title)
    title_layout.addWidget(subtitle)
    content_frame_layout.addWidget(title_container)

    # === 三個插槽區 ===
    intro_frame = QFrame()
    intro_layout = QVBoxLayout(intro_frame)

    page2_frame = QFrame()
    page2_layout = QVBoxLayout(page2_frame)

    page3_frame = QFrame()
    page3_layout = QVBoxLayout(page3_frame)

    content_frame_layout.addWidget(intro_frame)
    content_frame_layout.addWidget(page2_frame)
    content_frame_layout.addWidget(page3_frame)

    return {
        "widget": outer_wrapper,
        "slots": {
            "intro": intro_layout,
            "page2_help": page2_layout,
            "page3_help": page3_layout
        }
    }
