# Release Notes

## Version

0.4.0

## Release Date

2026-03-19

## What's New

- **Difficulty selection** (REQ-4): The main menu now shows three difficulty buttons — Easy (3x4), Normal (4x5), Hard (5x6) — instead of a single "New Game" button. Each starts a game with the corresponding board size and number of pairs.
- **Board size varies by difficulty** (REQ-4): Easy has 12 cards (6 pairs), Normal has 20 cards (10 pairs), Hard has 30 cards (15 pairs).
- **Randomized card placement** (REQ-4): Every round randomizes card positions, so repeated starts of the same difficulty produce different layouts.

### Previous releases

- **v0.3.0** — Real food artwork, square cards, asset manifest, 6 categories (REQ-3)
- **v0.2.0** — Card gameplay, flip animation, match/mismatch logic, input gating (REQ-2)
- **v0.1.0** — Desktop window, main menu, keyboard navigation, themes, persistent settings (REQ-1)

## Traceability

| REQ ID | AC IDs delivered | Version |
|---|---|---|
| REQ-1 | AC-1.1, AC-1.2, AC-1.3, AC-1.4 | v0.1.0 |
| REQ-2 | AC-2.1, AC-2.2, AC-2.3, AC-2.4, AC-2.5 | v0.2.0 |
| REQ-3 | AC-3.1, AC-3.2, AC-3.3, AC-3.4 | v0.3.0 |
| REQ-4 | AC-4.1, AC-4.2, AC-4.3 | v0.4.0 |

## Migration Notes

No migration steps required. Settings file format is unchanged.

## Known Issues

- The Continue button is always disabled (save/resume planned for REQ-6).
- Settings button does not transition to a settings screen yet (planned for REQ-7).
- Completing all matches currently does nothing visible — victory screen is planned for REQ-5.
- Default category is "dishes" — category selection from settings is planned for REQ-7.
- Only tested on Linux. Windows testing is deferred but no platform-specific APIs are used.

## User Guide

### Starting the game

```bash
pip install pygame pytest ruff
python -m src.main
```

### Playing

1. Choose a difficulty on the main menu: **Easy (3x4)**, **Normal (4x5)**, or **Hard (5x6)**
2. A grid of square face-down cards appears with diamond-patterned backs
3. Click a card (or use arrow keys + Enter/Space) to flip it — reveals food artwork
4. Flip a second card — if they match, both stay revealed
5. If they don't match, both flip back after a short delay
6. Find all pairs to complete the round
7. Press **Escape** to return to the main menu

### Keyboard controls

| Key | Menu | Game |
|---|---|---|
| Tab / Down | Next button | — |
| Shift+Tab / Up | Previous button | — |
| Arrow keys | — | Move cursor on grid |
| Enter / Space | Activate button | Flip card at cursor |
| Escape | Quit application | Return to main menu |

### Mouse

Click any card to flip it. Click menu buttons to activate them.

### Window resize

Drag the window edges to resize. All UI elements scale proportionally. Minimum size: 320x240.

## Release Archive

`releases/v0.4.0/release-v0.4.0.zip` — contains `src/`, `tests/`, `docs/REL.md`, `docs/REV.md`.
