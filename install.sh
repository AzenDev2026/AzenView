#!/usr/bin/env bash
# AzenView 安装脚本：Plasma 小组件（可固定到面板）+ 图标 + 应用菜单入口
# 全部写入用户目录，无需 sudo
set -e

cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

ICON_BASE="$HOME/.local/share/icons"
APP_BASE="$HOME/.local/share/applications"
PLASMOID_ID="com.azen.azenview"

echo "== AzenView 安装 =="

echo "[1/4] 安装图标..."
mkdir -p "$ICON_BASE"
if [ -d "assets/icons/hicolor" ]; then
    cp -r assets/icons/hicolor/. "$ICON_BASE/hicolor/"
    echo "      ✓ 图标已安装"
else
    echo "      ⚠ 未找到图标，先运行: python3 tools/make_icon.py"
fi

echo "[2/4] 安装 Plasma 小组件..."
if command -v kpackagetool6 >/dev/null 2>&1; then
    kpackagetool6 -t Plasma/Applet -i plasmoid >/dev/null 2>&1 || \
        kpackagetool6 -t Plasma/Applet -u plasmoid >/dev/null 2>&1
    echo "      ✓ 小组件已安装 ($PLASMOID_ID)"
else
    mkdir -p "$HOME/.local/share/plasma/plasmoids/$PLASMOID_ID"
    cp -r plasmoid/. "$HOME/.local/share/plasma/plasmoids/$PLASMOID_ID/"
    echo "      ✓ 小组件已复制到 ~/.local/share/plasma/plasmoids/$PLASMOID_ID"
fi

echo "[3/4] 写入应用菜单入口..."
mkdir -p "$APP_BASE"
cat > "$APP_BASE/azenview.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=AzenView
GenericName=Task View
Comment=AzenView - one-click KDE Overview (task view) button
Exec=$PROJECT_DIR/run.sh
Icon=azenview
Terminal=false
Categories=Utility;
Keywords=task;view;virtual;desktop;workspace;overview;
StartupWMClass=AzenView
EOF
echo "      ✓ 已写入 $APP_BASE/azenview.desktop"

echo "[4/4] 刷新桌面数据库..."
update-desktop-database "$APP_BASE" 2>/dev/null || true
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 2>/dev/null || true

echo ""
echo "✅ AzenView 安装完成！"
echo "   固定到任务栏：右键任务栏空白处 → 编辑面板 → 添加小组件 →"
echo "   搜索 AzenView → 添加（放在搜索框右边即可，像 Windows 任务视图）。"
