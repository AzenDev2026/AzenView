"""AzenView 覆盖层窗口：全屏展示所有虚拟桌面卡片，点击切换。"""

from PyQt6.QtCore import QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QKeyEvent, QPainter
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .card import DesktopCard
from .kwin import KWinBackend, KWinError


class OverlayWindow(QWidget):
    """无边框全屏覆盖层：桌面卡片流 + 点击切换 + Esc/空白点击关闭。"""

    # 需要重新加载桌面列表（由 main 的 QLocalServer 消息触发）
    show_requested = pyqtSignal()

    def __init__(self, kwin: KWinBackend):
        super().__init__(None)
        self.kwin = kwin
        self._cards: list[DesktopCard] = []
        self._windows = None
        self._windows_error = ""

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # ---- 布局 ----
        root = QVBoxLayout(self)
        root.setContentsMargins(60, 46, 60, 46)
        root.setSpacing(22)

        title = QLabel("Azen View", self)
        title.setStyleSheet("color: #e6e6e6; font-size: 26px; font-weight: 700;")
        root.addWidget(title)

        hint = QLabel("点击桌面卡片切换 · 点击空白处或按 Esc 关闭", self)
        hint.setStyleSheet("color: #9a9a9a; font-size: 12px;")
        root.addWidget(hint)

        self.cards_area = QWidget(self)
        self.cards_layout = QGridLayout(self.cards_area)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.cards_area, 1)

        # 弹出后稍等再加载（等 KWin 就绪），并定时刷新
        QTimer.singleShot(60, self.refresh)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(1500)
        self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start()

        kwin.desktops_changed.connect(self.refresh)
        kwin.current_changed.connect(self._on_current_changed)

    # ------------------------------------------------------------------
    def show_overlay(self):
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.geometry())
        self.refresh()
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    # ------------------------------------------------------------------
    def refresh(self):
        try:
            desktops = self.kwin.desktops()
        except KWinError:
            return
        current = ""
        try:
            current = self.kwin.current_id()
        except KWinError:
            pass

        # 窗口信息：查询失败（未授权）时优雅降级
        try:
            self._windows = self.kwin.windows()
            self._windows_error = ""
        except KWinError as exc:
            self._windows = None
            self._windows_error = str(exc)

        self._rebuild_cards(desktops, current)

    def _windows_for(self, desktop_id: str):
        if self._windows is None:
            return None
        result = []
        for w in self._windows:
            desktops = KWinBackend.window_desktops(w)
            if not desktops or bool(w.get("onAllDesktops")) or desktop_id in desktops:
                result.append(w)
        return result

    def _rebuild_cards(self, desktops: list[dict], current: str):
        # 清空旧卡片
        for card in self._cards:
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        if not desktops:
            return

        columns = 1 if len(desktops) <= 1 else min(len(desktops), 4)
        for i, desk in enumerate(desktops):
            card = DesktopCard(
                desk,
                self._windows_for(desk["id"]),
                desk["id"] == current,
                self.cards_area,
            )
            card.clicked.connect(lambda _checked=False, d=desk: self._switch(d))
            self._cards.append(card)
            self.cards_layout.addWidget(card, i // columns, i % columns)

    def _switch(self, desk: dict):
        try:
            self.kwin.switch_to(desk["id"])
        except KWinError:
            pass
        self.close()

    def _on_current_changed(self, _desktop_id: str):
        # 仅刷新卡片高亮，不重新查询窗口（避免频繁弹授权）
        self.refresh()

    # ------------------------------------------------------------------
    def paintEvent(self, _event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(32, 32, 32, 238))
        p.setPen(QColor(255, 255, 255, 26))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(QRectF(0.5, 0.5, self.width() - 1, self.height() - 1), 0, 0)
        p.end()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # 点击卡片时子控件会消费事件；落到这里说明点的是空白背景
        self.close()
