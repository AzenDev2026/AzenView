# AzenView 🖥️

A one-click **Task View button for KDE Plasma** — a real Plasma widget
(plasmoid) you can pin to the panel: click it and KWin's built-in
**Overview** effect pops up, exactly like pressing `Meta+W` and just like the
Windows task-view button.

> Plasma 6 plasmoid (QML) · triggers KWin over D-Bus · no daemons, tiny

## ✨ What it does

KDE Plasma already ships a full task-view (the *Overview* effect): it shows
every virtual desktop and all their windows, lets you **click a desktop to
switch**, **click a window to focus** it, and **drag windows across desktops**.

AzenView is the button for it — one click toggles the Overview open/closed,
ready to be pinned right next to the search box like on Windows.

## 📦 Install & pin to the panel

```bash
cd ~/Desktop/azenview
./install.sh      # installs the plasmoid + icon + app menu entry (no sudo)
```

Then: right-click the panel → **Edit Panel** → **Add Widgets** → search
**AzenView** → add it and drag it next to the search box.

## 🛠️ How it works

The plasmoid button runs:

```
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.toggleEffect overview
```

If Overview is disabled (System Settings → Desktop Effects → Overview), turn
it on — the widget also ships a standalone fallback (`run.sh`) that reports
problems with a dialog.

## 📁 Project structure

```
azenview/
├── plasmoid/                # The Plasma widget (this is the main thing)
│   ├── metadata.json        # KPackage metadata (id com.azen.azenview)
│   └── contents/ui/main.qml # Panel button → toggleEffect("overview")
├── main.py                  # Standalone fallback (CLI / app menu entry)
├── run.sh / install.sh
├── tools/make_icon.py       # Icon generator (two offset squares, ~75% overlap)
├── assets/                  # azenview.png + hicolor multi-size icons
└── azenview/
    ├── __init__.py          # App name & version
    └── kwin.py              # KWin D-Bus backend (Overview trigger)
```

## 🎨 Icon

Two equal rounded squares on a blue-purple gradient: the top one offset to the
top-right with ~75% overlap, styled like a little window card. Regenerate with
`python3 tools/make_icon.py` and re-run `./install.sh`.
