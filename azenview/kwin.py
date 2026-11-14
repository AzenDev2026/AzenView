"""KWin D-Bus 后端：虚拟桌面列表 / 切换 / 窗口信息。"""

import json

from PyQt6.QtCore import QObject, QVariant, pyqtSignal, pyqtSlot
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage

VDM_SERVICE = "org.kde.KWin"
VDM_PATH = "/VirtualDesktopManager"
VDM_IFACE = "org.kde.KWin.VirtualDesktopManager"
PROPS_IFACE = "org.freedesktop.DBus.Properties"


class KWinError(Exception):
    """KWin 拒绝请求（例如窗口信息查询需要用户授权）。"""


class KWinBackend(QObject):
    """封装 org.kde.KWin 的虚拟桌面管理接口。"""

    desktops_changed = pyqtSignal()
    current_changed = pyqtSignal(str)  # 新当前桌面 id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bus = QDBusConnection.sessionBus()
        self.vdm = QDBusInterface(
            VDM_SERVICE, VDM_PATH, VDM_IFACE, self.bus
        )

        # 虚拟桌面变化信号 → 界面刷新
        for signal in (
            "desktopCreated",
            "desktopRemoved",
            "desktopDataChanged",
            "rowsChanged",
        ):
            self.bus.connect(
                VDM_SERVICE, VDM_PATH, VDM_IFACE, signal, self._on_desktops_changed
            )
        self.bus.connect(
            VDM_SERVICE, VDM_PATH, VDM_IFACE, "currentChanged", self._on_current_changed
        )

    # ------------------------------------------------------------------
    @pyqtSlot()
    def _on_desktops_changed(self):
        self.desktops_changed.emit()

    @pyqtSlot(str)
    def _on_current_changed(self, desktop_id: str):
        self.current_changed.emit(desktop_id)

    # ------------------------------------------------------------------
    def _get_property(self, prop: str):
        """通过 Properties.Get 显式读取（QDBusInterface.property 不可靠）。"""
        msg = QDBusMessage.createMethodCall(
            VDM_SERVICE, VDM_PATH, PROPS_IFACE, "Get"
        )
        msg.setArguments([VDM_IFACE, prop])
        reply = self.bus.call(msg)
        if reply.errorName():
            raise KWinError(f"{reply.errorName()}: {reply.errorMessage()}")
        args = reply.arguments()
        return args[0] if args else None

    def _set_property(self, prop: str, value) -> None:
        msg = QDBusMessage.createMethodCall(
            VDM_SERVICE, VDM_PATH, PROPS_IFACE, "Set"
        )
        msg.setArguments([VDM_IFACE, prop, QVariant(value)])
        reply = self.bus.call(msg)
        if reply.errorName():
            raise KWinError(f"{reply.errorName()}: {reply.errorMessage()}")

    # ------------------------------------------------------------------
    def desktops(self) -> list[dict]:
        """返回 [{"id", "name", "position"}]，按 position 排序。"""
        raw = self._get_property("desktops")  # a(uss): (position, id, name)
        if raw is None:
            return []
        items = []
        for entry in raw:
            items.append(
                {
                    "position": int(entry[0]),
                    "id": str(entry[1]),
                    "name": str(entry[2]),
                }
            )
        items.sort(key=lambda d: d["position"])
        return items

    def current_id(self) -> str:
        value = self._get_property("current")
        return str(value) if value is not None else ""

    def switch_to(self, desktop_id: str) -> None:
        """切换到指定虚拟桌面（写 current 属性）。"""
        self._set_property("current", desktop_id)

    # ------------------------------------------------------------------
    def toggle_overview(self) -> bool:
        """弹出/收起 KWin 自带的 Overview（任务视图）。

        优先使用 Effects.toggleEffect("overview")；失败时回退到
        触发 kglobalaccel 的 "Overview" 全局快捷键（等同按 Meta+W）。
        返回是否成功。
        """
        iface = QDBusInterface(
            "org.kde.KWin", "/Effects", "org.kde.kwin.Effects", self.bus
        )
        if not iface.isValid():
            return False

        # 确保效果已加载
        reply = iface.call("isEffectLoaded", "overview")
        if reply.errorName() or not reply.arguments():
            return False
        if not reply.arguments()[0]:
            load = iface.call("loadEffect", "overview")
            if load.errorName():
                return False

        toggle = iface.call("toggleEffect", "overview")
        if not toggle.errorName():
            return True

        # 回退：kglobalaccel 触发 Overview 快捷键
        kglobal = QDBusInterface(
            "org.kde.kglobalaccel",
            "/component/kwin",
            "org.kde.kglobalaccel.Component",
            self.bus,
        )
        if kglobal.isValid():
            invoke = kglobal.call("invokeShortcut", "Overview")
            return not invoke.errorName()
        return False

    # ------------------------------------------------------------------
    def windows(self) -> list[dict]:
        """所有窗口的原始信息列表。

        KWin 6 在 Wayland 下首次查询会弹授权对话框，用户取消时抛
        KWinError("UserCancel")。
        """
        result = self.vdm.call("queryWindowInfo")
        if result.errorName():
            raise KWinError(
                f"{result.errorName()}: {result.errorMessage()}"
            )
        args = result.arguments()
        if not args:
            return []
        win_map = args[0]  # QVariantMap: {uuid: json-string}
        windows = []
        for value in win_map.values():
            if isinstance(value, str):
                try:
                    windows.append(json.loads(value))
                except json.JSONDecodeError:
                    continue
            elif isinstance(value, dict):
                windows.append(value)
        return windows

    # ------------------------------------------------------------------
    @staticmethod
    def window_title(window: dict) -> str:
        """防御性解析窗口标题（KWin 各版本字段名略有差异）。"""
        for key in ("caption", "title", "name"):
            value = window.get(key)
            if value:
                return str(value)
        return ""

    @staticmethod
    def window_desktops(window: dict) -> list[str]:
        """窗口所在的虚拟桌面 id 列表。"""
        value = window.get("desktops") or window.get("desktop")
        if value is None:
            return []
        if isinstance(value, list):
            return [str(v) for v in value]
        return [str(value)]

    @staticmethod
    def window_geometry(window: dict) -> dict | None:
        """窗口几何 {x, y, width, height}，解析失败返回 None。"""
        geo = window.get("geometry")
        if not isinstance(geo, dict):
            # 某些版本平铺在顶层
            geo = {k: window.get(k) for k in ("x", "y", "width", "height")}
        try:
            return {
                "x": float(geo["x"]),
                "y": float(geo["y"]),
                "width": max(float(geo["width"]), 1.0),
                "height": max(float(geo["height"]), 1.0),
            }
        except (KeyError, TypeError, ValueError):
            return None

    @staticmethod
    def window_class(window: dict) -> str:
        """应用类别（用于预览块配色），如 "dolphin"、"firefox"。"""
        for key in ("resourceClass", "resourceName", "appId"):
            value = window.get(key)
            if value:
                return str(value).lower()
        return ""
