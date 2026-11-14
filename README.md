# AzenView 🖥️

A Windows-Task-View-style **virtual desktop switcher** for KDE Plasma: click the
panel icon, see every virtual desktop as a preview card, click a card to switch.

> Python 3 + PyQt6 · talks to KWin over D-Bus · no sudo, no daemons

## ✨ Features (v0.1.0)

- **All virtual desktops at a glance** — an overlay showing one card per
  virtual desktop (KWin `VirtualDesktopManager`)
- **Window layout preview** — each card draws a miniature layout of the
  windows living on that desktop (geometry-based schematic, color-coded by
  app, minimized windows shown dimmed)
- **One-click switching** — click a card to jump to that desktop
  (`Properties.Set current`), `Esc` or click outside to close
- **Live updates** — cards refresh when desktops are created/removed/renamed
  or the current desktop changes
- **Current desktop badge** — the active desktop's card is highlighted
- **Single instance** — clicking the panel icon again just brings the
  existing overlay back
- **Privacy aware** — window info requires a one-time KWin permission prompt
  on Wayland; if declined, cards gracefully fall back to name-only

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

## ⌨️ Interactions

| Action | Result |
| --- | --- |
| Click a card | Switch to that virtual desktop & close |
| `Esc` | Close the overlay |
| Click empty area | Close the overlay |

## 🛠️ Tech notes

- Desktop list / current desktop: `org.kde.KWin.VirtualDesktopManager`
  (read via explicit `org.freedesktop.DBus.Properties.Get` — PyQt6's
  `QDBusInterface.property()` proved unreliable here)
- Window info: `org.kde.KWin.queryWindowInfo` (JSON per window: caption,
  geometry, desktops, resourceClass, minimized, …)
- Switching: write `current` on the VirtualDesktopManager (desktop UUID)

## 📁 Project structure

```
azenview/
├── main.py                 # Entry point (single-instance via QLocalServer)
├── run.sh / install.sh
├── tools/make_icon.py      # Icon generator (two overlapping windows)
├── assets/                 # azenview.png + hicolor multi-size icons
└── azenview/
    ├── __init__.py         # App name & version
    ├── kwin.py             # KWin D-Bus backend
    ├── card.py             # Desktop card widget (layout preview painting)
    └── overlay.py          # Fullscreen overlay window
```

## 🗺️ Roadmap

- Real live thumbnails via KWin effects / ScreenCast portal
- Create / remove / rename desktops from the overlay
- Global shortcut (e.g. Ctrl+Alt+Tab)
- Drag windows between desktops
