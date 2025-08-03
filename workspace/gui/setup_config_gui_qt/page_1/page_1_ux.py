from PyQt5.QtWidgets import QFrame, QLabel, QTextBrowser, QVBoxLayout, QSizePolicy, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


def build_card(title_text: str, html_body: str, icon: str = "💬") -> QFrame:
    class HoverFrame(QFrame):
        def __init__(self):
            super().__init__()
            self._shadow_effect = None
            self._effect_active = False

        def enterEvent(self, event):
            if not self._effect_active:
                self._shadow_effect = QGraphicsDropShadowEffect()
                self._shadow_effect.setBlurRadius(15)
                self._shadow_effect.setOffset(0, 0)
                self._shadow_effect.setColor(QColor(255, 255, 255, 40))
                self.setGraphicsEffect(self._shadow_effect)
                self._effect_active = True

        def leaveEvent(self, event):
            self.setGraphicsEffect(None)
            self._effect_active = False

    card = HoverFrame()
    card.setStyleSheet("""
        QFrame {
            background-color: rgba(40, 40, 40, 0.7);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
    """)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
    card.setMinimumHeight(170)

    layout = QVBoxLayout(card)
    layout.setSpacing(12)

    # ✅ 完全不使用 HTML，避免 stylesheet 衝突
    title = QLabel(f"{icon} {title_text}")
    title.setAlignment(Qt.AlignLeft)
    title.setTextFormat(Qt.PlainText)
    title.setStyleSheet("""
        font-size: 16px;
        font-weight: bold;
        color: #ffffff;
    """)
    layout.addWidget(title)

    # ✅ 文字內容區
    text = QTextBrowser()
    text.setOpenExternalLinks(True)
    text.setMinimumHeight(72)
    text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    text.setStyleSheet("""
        QTextBrowser {
            border: none;
            background: transparent;
            font-size: 13px;
            color: #dddddd;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
        }
        QScrollBar::handle:vertical {
            background: #888;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }
    """)
    text.setHtml(html_body)
    layout.addWidget(text)

    return card



def get_intro_card() -> QFrame:
    html = """
    <p>本工具為測試人員設計，協助自動化執行「限紅測試流程」，並自動產出測試報表。</p>
    <p>僅需輸入測試所需參數，即可完成運行與比對。</p>
    """
    return build_card("工具簡介", html, icon="🧰")


def get_page2_help_card() -> QFrame:
    html = """
    <style>
        * { font-size: 13px; line-height: 1.5; }
        table { width: 100%; table-layout: fixed; }
        td { vertical-align: top; padding: 4px 16px 4px 0; }
        h4 {
            color: #80cbc4;
            margin: 0 0 4px 0;
            font-size: 14px;
            font-weight: bold;
        }
        ul {
            margin: 2px 0 6px 18px;
            padding: 0;
        }
        p {
            margin: 0 0 6px 0;
        }
    </style>
    <table>
      <tr>
        <td>
          <h4>🔹 PF_ID</h4>
          <p>由測試單提供，請確認目前測試案例使用之平台編號。</p>

          <h4>🔹 限紅邏輯模式</h4>
          <ul>
            <li><b>最大限紅：</b> 如「最高限紅為 200」</li>
            <li><b>最小限紅：</b> 如「最低限紅為 200」</li>
          </ul>
        </td>
        <td>
          <h4>🔹 PRIVATE_KEY</h4>
          <p>請至 <i>後台 → 系統管理 → 平台管理</i>，以 PF_ID 查詢對應的金鑰。</p>

          <h4>🔹 限紅規則運算</h4>
          <ul>
            <li><b>「最低限紅為 200」</b> → 設定為 <code>>= 200</code> 或 <code>== 200</code></li>
          </ul>
        </td>
      </tr>
    </table>
    """
    return build_card("Page2：參數設定說明", html, icon="⚙️")


def get_page3_help_card() -> QFrame:
    html = """
    <style>
        * { font-size: 13px; line-height: 1.5; }
        table { width: 100%; table-layout: fixed; }
        td { vertical-align: top; padding: 4px 16px 4px 0; }
        h4 {
            color: #81c784;
            font-size: 14px;
            margin: 4px 0 6px 0;
            font-weight: bold;
        }
        ul {
            margin: 4px 0 10px 18px;
            padding: 0;
        }
        li {
            margin-bottom: 4px;
        }
        b {
            color: #ffee58;
        }
    </style>

    <table>
      <tr>
        <td>
          <h4>📄 測試報表查看</h4>
          <ul>
            <li>執行 <b>ALL</b> 流程完成後，點選「查看測試報表」以檢視限紅測試結果</li>
            <li>若按鈕無法點擊，請確認是否已執行完成，並無報錯</li>
          </ul>
        </td>
        <td>
          <h4>❗️ 除錯與協助</h4>
          <ul>
            <li>若測試報告顯示 <b>None</b>、或執行過程發生錯誤，請：</li>
            <li>① 勾選 <b>DEBUG 模式</b> 並重新執行</li>
            <li>② 點選「匯出執行記錄」並將產出檔案傳給開發人員</li>
          </ul>
        </td>
      </tr>
    </table>
    """
    return build_card("Page3：執行測試說明", html, icon="🚀")
