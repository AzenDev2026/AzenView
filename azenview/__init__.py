"""AzenView — 任务栏按钮，一键唤起 KDE Plasma 自带的 Overview（任务视图）。

点击面板上的 AzenView 图标，即可弹出/收起 KWin Overview：
看到所有虚拟桌面和窗口、点击桌面切换、拖拽窗口跨桌面——与按 Meta+W 完全一致。

实现：通过 D-Bus 调用 org.kde.KWin /Effects 的 toggleEffect("overview")，
失败时回退到 kglobalaccel 的 "Overview" 全局快捷键。
"""

APP_NAME = "AzenView"
APP_VERSION = "0.2.0"
