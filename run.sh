#!/usr/bin/env bash
# AzenView 启动脚本（使用系统 PyQt6）
cd "$(dirname "$0")"

# 检查 PyQt6 是否可用
python3 -c "import PyQt6.QtDBus" 2>/dev/null || {
    echo "缺少 PyQt6，请先安装：sudo pacman -S python-pyqt6"
    exit 1
}

exec python3 main.py "$@"
