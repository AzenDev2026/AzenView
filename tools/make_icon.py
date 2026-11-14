"""生成 AzenView 图标（多尺寸 PNG）：任务视图风格的两个重叠窗口。

运行：python3 tools/make_icon.py（使用系统 PyQt6）
输出：assets/azenview.png（窗口图标）
      assets/icons/hicolor/<size>/apps/azenview.png（安装用）
"""

from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QImage, QLinearGradient, QPainter, QPen

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
HICOLOR = ASSETS / "icons" / "hicolor"

SIZES = (512, 256, 128, 64, 48, 32, 24, 16)


def render(size: int) -> QImage:
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    s = size / 512.0

    # ---- 渐变圆角底（Azen 蓝 → 紫） ----
    grad = QLinearGradient(0, 0, 512 * s, 512 * s)
    grad.setColorAt(0.0, QColor("#3d7bff"))
    grad.setColorAt(1.0, QColor("#8a5cf6"))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(grad))
    p.drawRoundedRect(QRectF(4 * s, 4 * s, 504 * s, 504 * s), 118 * s, 118 * s)

    # ---- 后窗口（白色半透明，偏右上） ----
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(255, 255, 255, 120))
    p.drawRoundedRect(QRectF(172 * s, 96 * s, 244 * s, 300 * s), 56 * s, 56 * s)

    # ---- 前窗口（白色，偏左下，带内容线条） ----
    p.setBrush(QColor("#f4f6fa"))
    p.drawRoundedRect(QRectF(96 * s, 142 * s, 244 * s, 300 * s), 56 * s, 56 * s)

    # 前窗口的标题条与内容线
    p.setPen(QPen(QColor("#5a6b8c"), 16 * s))
    p.drawLine(QPointF(130 * s, 184 * s), QPointF(306 * s, 184 * s))   # 标题线
    p.setPen(QPen(QColor("#c3ccdb"), 14 * s))
    p.drawLine(QPointF(130 * s, 236 * s), QPointF(306 * s, 236 * s))   # 内容线 1
    p.setPen(QPen(QColor("#d4dae6"), 14 * s))
    p.drawLine(QPointF(130 * s, 276 * s), QPointF(260 * s, 276 * s))   # 内容线 2（短）
    p.setPen(QPen(QColor("#e2e7ef"), 14 * s))
    p.drawLine(QPointF(130 * s, 316 * s), QPointF(280 * s, 316 * s))   # 内容线 3

    p.end()
    return img


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        img = render(size)
        out_dir = HICOLOR / f"{size}x{size}" / "apps"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "azenview.png"
        img.save(str(out))
        print(f"✓ {out.relative_to(ROOT)}")
    window_icon = ASSETS / "azenview.png"
    render(256).save(str(window_icon))
    print(f"✓ {window_icon.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
