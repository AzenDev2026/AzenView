"""AzenView — KDE 任务视图：虚拟桌面预览与一键切换。

类似 Windows 的任务视图（Task View）：弹出所有虚拟桌面的预览卡片，
点击卡片即可切换到对应桌面。

技术：Python + PyQt6，通过 KWin D-Bus 接口
（org.kde.KWin.VirtualDesktopManager / org.kde.KWin）获取与切换虚拟桌面。
"""

APP_NAME = "AzenView"
APP_VERSION = "0.1.0"
