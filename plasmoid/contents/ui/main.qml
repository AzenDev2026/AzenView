/*
 * AzenView plasmoid — 面板按钮，点击唤起/收起 KWin Overview（任务视图）。
 * 通过 org.kde.kwin.Effects.toggleEffect("overview") 触发，等同按 Meta+W。
 */
import QtQuick
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PlasmaComponents3

PlasmoidItem {
    id: root

    switchWidth: PlasmaCore.Units.iconSizes.smallMedium
    switchHeight: PlasmaCore.Units.iconSizes.smallMedium

    toolTipMainText: "AzenView"
    toolTipSubText: "切换任务视图 (Overview)"

    // 执行系统命令（点击按钮时触发 toggleEffect）
    PlasmaCore.DataSource {
        id: executable
        engine: "executable"
        connectedSources: []
        onNewData: disconnectSource(sourceName)
    }

    fullRepresentation: PlasmaComponents3.ToolButton {
        Layout.minimumWidth: PlasmaCore.Units.iconSizes.smallMedium
        Layout.minimumHeight: PlasmaCore.Units.iconSizes.smallMedium
        icon.name: "azenview"
        Accessible.name: "AzenView"

        onClicked: executable.connectSource(
            "qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.toggleEffect overview"
        )
    }
}
