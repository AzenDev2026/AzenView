"""AzenView 入口：触发 KWin 自带的 Overview（任务视图）。"""

import sys

from PyQt6.QtWidgets import QApplication

from azenview import APP_NAME, APP_VERSION
from azenview.kwin import KWinBackend


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    kwin = KWinBackend()
    if kwin.toggle_overview():
        # 成功触发（弹出或收起 KWin Overview），立即退出
        return 0

    # 失败时短暂停留并报错（stderr 会被面板吞掉，这里用图形提示更友好）
    from PyQt6.QtWidgets import QMessageBox

    QMessageBox.critical(
        None,
        "AzenView",
        "无法触发 KWin Overview。\n\n"
        "请确认你正在使用 KDE Plasma 会话，\n"
        "且系统设置 → 桌面效果 → Overview 没有被禁用。",
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
