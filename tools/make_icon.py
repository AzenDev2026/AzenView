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

    # ---- 两个等大的方块，上方向右上偏移，重叠约 75% ----
    # 边长 280；偏移 d = 280 × (1 − √0.75) ≈ 40
    side = 280.0
    d = 40.0
    ax, ay = 96.0, 161.0                    # 下方块（左）
    bx, by = ax + d, ay - d                 # 上方块（右上偏移）

    # 下方块：白色半透明
    p.setBrush(QColor(255, 255, 255, 125))
    p.drawRoundedRect(QRectF(ax * s, ay * s, side * s, side * s), 60 * s, 60 * s)

    # 上方块：白色实底 + 窗口内容线
    p.setBrush(QColor("#f4f6fa"))
    p.drawRoundedRect(QRectF(bx * s, by * s, side * s, side * s), 60 * s, 60 * s)

    p.setPen(QPen(QColor("#5a6b8c"), 16 * s))
    p.drawLine(QPointF((bx + 34) * s, (by + 44) * s),
               QPointF((bx + 226) * s, (by + 44) * s))          # 标题线
    p.setPen(QPen(QColor("#c3ccdb"), 14 * s))
    p.drawLine(QPointF((bx + 34) * s, (by + 96) * s),
               QPointF((bx + 246) * s, (by + 96) * s))          # 内容线 1
    p.setPen(QPen(QColor("#d4dae6"), 14 * s))
    p.drawLine(QPointF((bx + 34) * s, (by + 136) * s),
               QPointF((bx + 190) * s, (by + 136) * s))         # 内容线 2（短）
    p.setPen(QPen(QColor("#e2e7ef"), 14 * s))
    p.drawLine(QPointF((bx + 34) * s, (by + 176) * s),
               QPointF((bx + 216) * s, (by + 176) * s))         # 内容线 3

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
