# AzenView 🖥️ — ARCHIVED

> ⚠️ **This project is archived and does NOT work.**
> The repository is kept for reference only. Please do not expect it to run.

---

AzenView was an attempt at a Windows-Task-View-style button for KDE Plasma:
a panel widget that would open a virtual-desktop overview and let you switch
desktops with one click.

## What was tried

| Version | Approach | Result |
| --- | --- | --- |
| v0.1.0 | Custom PyQt6 overlay with desktop cards and a window-layout preview | Desktop switching did not work reliably |
| v0.2.0 | Trigger KWin's built-in **Overview** effect via D-Bus (`toggleEffect("overview")`) | Trigger worked, but the `.desktop` app could not be added through the panel's "Add Widgets" dialog |
| v0.3.x | Converted to a real Plasma plasmoid (`com.azen.azenview`) | plasmashell (Plasma 6.8) rejected the widget with "unsupported Plasma version" and this was never resolved |

The project was abandoned on 2026-11-14.

## Use the built-in features instead

KDE Plasma already provides everything this project wanted:

- **`Meta+W`** — open the Overview (all virtual desktops and windows, click to switch)
- **`Ctrl+F1` / `Ctrl+F2`** — switch directly to desktop 1 / 2
- **System Settings → Desktop Effects → Overview** — customize its look and animation
- **System Settings → Workspace → Hot Corners** — trigger Overview from a screen corner

## Code

The source remains in this repository for reference:
`plasmoid/` (QML widget), `main.py` (standalone D-Bus trigger),
`azenview/kwin.py` (KWin D-Bus helpers), `tools/make_icon.py` (icon generator).
