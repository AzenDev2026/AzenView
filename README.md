# AzenView 🖥️

A one-click **Task View button for KDE Plasma**: pin it to your panel, click
it, and KWin's built-in **Overview** effect pops up — exactly like pressing
`Meta+W`, and just like the Windows task-view button.

> Python 3 + PyQt6 · triggers KWin over D-Bus · tiny, no daemons, no UI of its own

## ✨ What it does

KDE Plasma already ships a full task-view (the *Overview* effect): it shows
every virtual desktop, all their windows, lets you **click a desktop to
switch**, **click a window to focus** it, and **drag windows across desktops**.

AzenView is just the convenient button for it — one click toggles the
Overview open/closed, so you can pin it right next to the search box like on
Windows.

## 🚀 Running

```bash
cd ~/Desktop/azenview
./run.sh          # uses the system PyQt6 (Arch: sudo pacman -S python-pyqt6)
```

## 📦 Install & pin to the panel

```bash
cd ~/Desktop/azenview
./install.sh      # installs icon + app menu entry (user directory, no sudo)
```

Then: right-click the panel → Edit Panel → Add Widgets → search
**AzenView** → add it (place it next to the search box, like Windows).

## 🛠️ How it works

1. Calls `org.kde.KWin /Effects` → `isEffectLoaded("overview")`;
   loads the effect first if it isn't loaded
2. Calls `toggleEffect("overview")` to pop the Overview open or closed
3. Fallback: invokes the `Overview` global shortcut through
   `org.kde.kglobalaccel` (same as pressing `Meta+W`)

If Overview is disabled (System Settings → Desktop Effects → Overview),
AzenView shows a small dialog explaining what to enable.

## 📁 Project structure

```
azenview/
├── main.py                 # Entry point: trigger Overview, then exit
├── run.sh / install.sh
├── tools/make_icon.py      # Icon generator (two overlapping windows)
├── assets/                 # azenview.png + hicolor multi-size icons
└── azenview/
    ├── __init__.py         # App name & version
    └── kwin.py             # KWin D-Bus backend (Overview + desktop info)
```
