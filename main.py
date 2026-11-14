"""AzenView 启动入口：单实例 + 任务视图覆盖层。"""

import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtWidgets import QApplication

from azenview import APP_NAME, APP_VERSION
from azenview.kwin import KWinBackend
from azenview.overlay import OverlayWindow

SOCKET_NAME = "azenview-single"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setDesktopFileName("azenview")

    icon_path = ASSETS_DIR / "azenview.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # ---- 单实例：已有实例在运行 → 让它显示，本进程退出 ----
    probe = QLocalSocket()
    probe.connectToServer(SOCKET_NAME)
    if probe.waitForConnected(150):
        probe.write(b"show")
        probe.flush()
        probe.waitForBytesWritten(200)
        probe.disconnectFromServer()
        return 0

    QLocalServer.removeServer(SOCKET_NAME)
    server = QLocalServer()
    server.listen(SOCKET_NAME)

    kwin = KWinBackend()
    overlay = OverlayWindow(kwin)

    def handle_message(conn, ov):
        if conn.readAll().data() == b"show":
            ov.show_overlay()

    def on_connection():
        while server.hasPendingConnections():
            conn = server.nextPendingConnection()
            conn.readyRead.connect(lambda c=conn: handle_message(c, overlay))

    server.newConnection.connect(on_connection)

    app.setQuitOnLastWindowClosed(False)
    overlay.show_overlay()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
