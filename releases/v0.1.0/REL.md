# Release Notes

## Version

0.1.0

## Release Date

2026-03-19

## What's New

- **Desktop window and main menu** (REQ-1): launch the Delicious Memory game to see a resizable window with a main menu. Four buttons — New Game, Continue (disabled until a save exists), Settings, and Quit — are navigable by keyboard (Tab, arrows, Enter, Escape) and mouse. The window scales proportionally on resize, survives alt-tab without corruption, and quits cleanly.
- **Light and dark themes** (REQ-1): the application ships with a light theme (default) and a dark theme built from a branded green color palette. Theme switching infrastructure is in place for future bundles.
- **Persistent settings** (REQ-1): user preferences (theme, difficulty, sound, category) are saved to a JSON config file in the platform-appropriate directory and restored on next launch. Corrupt or missing config files fall back to defaults silently.

## Traceability

| REQ ID | AC IDs delivered | Commit(s) |
|---|---|---|
| REQ-1 | AC-1.1, AC-1.2, AC-1.3, AC-1.4 | 1480a33 |

## Migration Notes

No migration steps required. This is the initial release.

## Known Issues

- The Continue button is always disabled (save/resume is not yet implemented — planned for REQ-6).
- New Game and Settings buttons do not transition to their screens yet (gameplay and settings screens are planned for REQ-2 and REQ-7).
- Only tested on Linux. Windows testing is deferred but no platform-specific APIs are used.

## User Guide

### Starting the game

```bash
pip install pygame
python -m src.main
```

### Keyboard navigation

| Key | Action |
|---|---|
| Tab / Down | Move focus to next button |
| Shift+Tab / Up | Move focus to previous button |
| Enter | Activate focused button |
| Escape | Quit the application |

### Mouse

Click any enabled button to activate it.

### Window resize

Drag the window edges to resize. All UI elements scale proportionally. Minimum size: 320x240.

## Release Archive

`releases/v0.1.0/release-v0.1.0.zip` — contains `src/`, `docs/REL.md`, `docs/REV.md`.
