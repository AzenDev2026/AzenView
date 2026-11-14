"""桌面卡片：展示单个虚拟桌面的名称与窗口布局预览。"""

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from .kwin import KWinBackend

ACCENT = QColor("#4d8dff")


def _hash_color(name: str) -> QColor:
    """按应用名生成稳定的柔和色块颜色。"""
    if not name:
        return QColor("#5a6068")
    h = sum(ord(c) * (i + 31) for i, c in enumerate(name)) % 360
    return QColor.fromHsv(h, 140, 225)


class DesktopCard(QWidget):
    """一个虚拟桌面卡片。

    windows: 该桌面上的窗口列表（None 表示无授权/查询失败）。
    """

    CARD_W = 280
    CARD_H = 208
    PREVIEW_H = 158

    clicked = pyqtSignal()

    def __init__(self, desktop: dict, windows, is_current: bool, parent=None):
        super().__init__(parent)
        self.desktop = desktop
        self.windows = windows
        self.is_current = is_current
        self._hover = False
        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"切换到「{desktop['name']}」")

    # ------------------------------------------------------------------
    def enterEvent(self, event):
        self._hover = True
        self.update()

    def leaveEvent(self, event):
        self._hover = False
        self.update()

    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.position().toPoint())
        ):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ---- 卡片底 ----
        card = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        if self.is_current:
            p.setPen(QPen(ACCENT, 3))
            p.setBrush(QColor("#2b2b2b"))
        elif self._hover:
            p.setPen(QPen(QColor("#4d4d4d"), 2))
            p.setBrush(QColor("#262626"))
        else:
            p.setPen(QPen(QColor("#383838"), 1))
            p.setBrush(QColor("#232323"))
        p.drawRoundedRect(card, 16, 16)

        # ---- 预览区 ----
        preview = QRectF(10, 10, self.width() - 20, self.PREVIEW_H - 10)
        p.setPen(QPen(QColor("#383838"), 1))
        p.setBrush(QColor("#1c1c1c"))
        p.drawRoundedRect(preview, 10, 10)

        self._draw_windows(p, preview)
        self._draw_badge(p)

        # ---- 名称与窗口数 ----
        p.setPen(QColor("#e6e6e6"))
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        p.setFont(name_font)
        p.drawText(
            QRectF(14, self.PREVIEW_H + 6, self.width() - 80, 22),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.desktop["name"],
        )
        p.setPen(QColor("#9a9a9a"))
        small = QFont()
        small.setPointSize(8)
        p.setFont(small)
        if self.windows is None:
            count_text = "需要授权查看窗口"
        else:
            n = len(self.windows)
            count_text = f"{n} 个窗口" if n else "空桌面"
        p.drawText(
            QRectF(14, self.PREVIEW_H + 26, self.width() - 28, 18),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            count_text,
        )
        p.end()

    # ------------------------------------------------------------------
    def _draw_windows(self, p: QPainter, preview: QRectF):
        if not self.windows:
            return
        # 用所有窗口几何的并集做归一化基准
        geos = []
        for w in self.windows:
            geo = KWinBackend.window_geometry(w)
            if geo:
                geos.append(geo)
        if not geos:
            return
        min_x = min(g["x"] for g in geos)
        min_y = min(g["y"] for g in geos)
        max_x = max(g["x"] + g["width"] for g in geos)
        max_y = max(g["y"] + g["height"] for g in geos)
        span_w = max(max_x - min_x, 1.0)
        span_h = max(max_y - min_y, 1.0)

        pad = 10.0
        area = preview.adjusted(pad, pad, -pad, -pad)
        scale = min(area.width() / span_w, area.height() / span_h)

        title_font = QFont()
        title_font.setPointSize(7)

        for w, geo in zip(self.windows, geos):
            rw = geo["width"] * scale
            rh = geo["height"] * scale
            rx = area.x() + (geo["x"] - min_x) * scale
            ry = area.y() + (geo["y"] - min_y) * scale
            # 微调：预览图在区域里居中
            used_w = span_w * scale
            used_h = span_h * scale
            rx += (area.width() - used_w) / 2
            ry += (area.height() - used_h) / 2

            color = _hash_color(KWinBackend.window_class(w))
            minimized = bool(w.get("minimized"))
            if minimized:
                color.setAlpha(110)
            p.setPen(QPen(color.darker(120), 1))
            p.setBrush(color)
            p.drawRoundedRect(QRectF(rx, ry, max(rw, 8), max(rh, 8)), 3, 3)

            # 块足够大时写窗口标题
            if rw > 46 and rh > 18:
                p.setPen(QColor("#101010"))
                p.setFont(title_font)
                p.drawText(
                    QRectF(rx + 4, ry + 1, rw - 8, rh - 2),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    KWinBackend.window_title(w) or "窗口",
                )

    def _draw_badge(self, p: QPainter):
        if not self.is_current:
            return
        badge = QRectF(self.width() - 66, 18, 52, 22)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(ACCENT)
        p.drawRoundedRect(badge, 11, 11)
        p.setPen(QColor("#ffffff"))
        f = QFont()
        f.setPointSize(8)
        f.setBold(True)
        p.setFont(f)
        p.drawText(badge, Qt.AlignmentFlag.AlignCenter, "当前")
