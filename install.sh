#!/usr/bin/env bash
# AzenView 安装脚本：应用菜单入口 + 图标（全部在用户目录，无需 sudo）
set -e

cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

ICON_BASE="$HOME/.local/share/icons"
APP_BASE="$HOME/.local/share/applications"

echo "== AzenView 安装 =="

echo "[1/3] 安装图标..."
mkdir -p "$ICON_BASE"
if [ -d "assets/icons/hicolor" ]; then
    cp -r assets/icons/hicolor/. "$ICON_BASE/hicolor/"
    echo "      ✓ 图标已安装"
else
    echo "      ⚠ 未找到图标，先运行: python3 tools/make_icon.py"
fi

echo "[2/3] 写入应用菜单入口..."
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
Keywords=task;view;virtual;desktop;workspace;
StartupWMClass=AzenView
EOF
echo "      ✓ 已写入 $APP_BASE/azenview.desktop"

echo "[3/3] 刷新桌面数据库..."
update-desktop-database "$APP_BASE" 2>/dev/null || true
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 2>/dev/null || true

echo ""
echo "✅ AzenView 安装完成！"
echo "   固定到任务栏：右键任务栏空白处 → 编辑面板 → 添加小组件 →"
echo "   搜索 AzenView → 添加（放在你想要的位置，比如搜索框右边）。"
