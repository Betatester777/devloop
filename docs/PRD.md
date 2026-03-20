# Product Requirements Document

## Overview

**Delicious Memory** is a Python-based interactive desktop memory matching game themed around delicious dishes, dining, and drinks. Players flip colorful cards on a grid to find matching pairs of food artwork, with multiple difficulty levels, scoring, timed play, save/resume capability, and configurable sound and visual themes. The game targets Linux and Windows using pygame.

## Scope

This work includes:

- A card-based memory matching game with flip animations and match/mismatch logic
- Food-themed image categories loaded dynamically from asset subfolders
- Category selection in the settings screen
- Three difficulty levels (easy, normal, hard) controlling board size and card count
- Score tracking (move counter and score formula) and a countdown timer mode
- Victory and fail/retry screens with summary statistics
- Save and resume functionality with graceful corruption handling
- Sound effects for game events (flip, match, mismatch, win, lose) with mute/persist
- Light and dark color themes using a branded green palette with neutrals; light theme is the default
- Reduced-animation accessibility mode
- Full keyboard navigation with visible focus indicator
- Responsive window resizing and clean application lifecycle
- Asset manifest documenting all shipped images with source URL and license
- Cross-platform support for Linux and Windows

## Feature Bundles

| ID | Bundle | Description | Status |
|---|---|---|---|
| REQ-1 | Desktop UI and window | Application window, main menu, responsive resize, clean quit, focus-switch stability | Done |
| REQ-2 | Card gameplay | Grid of face-down cards, flip animation, match/mismatch logic, input gating during animation | Done |
| REQ-3 | Food-themed content | Dynamic category loading from asset subfolders, random image assignment to cards, asset manifest | Done |
| REQ-4 | Difficulty levels | Easy/normal/hard modes with varying board sizes, difficulty selection from main menu, randomized placement | Done |
| REQ-5 | Score and timer | Move counter, score formula, countdown timer, fail/retry screen on expiry, victory summary screen | Pending |
| REQ-6 | Save and resume | Mid-round save, restore full state on relaunch, disabled continue when no save exists, corrupted-save handling | Pending |
| REQ-7 | Sound and theme settings | Settings menu, sound effects, mute toggle with persistence, category selection, light/dark themes with brand palette, default light theme, reduced-animation mode | Pending |
| REQ-8 | Performance | Acceptable startup time, smooth frame rate, immediate input response | Pending |
| REQ-9 | Reliability | Crash-free 30-60 min sessions, no save corruption, no blocked progression, correct state reset on rapid restarts | Pending |
| REQ-10 | Usability | Intuitive first-play experience, readable text across all themes, clear result screens | Pending |
| REQ-11 | Accessibility | Full keyboard-only play, visible focus indicator, acceptable color contrast in all themes, audio not required for core gameplay | Pending |

## Acceptance Criteria

### REQ-1: Desktop UI and window

| ID | Criterion | Testable? |
|---|---|---|
| AC-1.1 | Given the application is launched, when the main window opens, then the main menu is displayed without crash or error. | Yes |
| AC-1.2 | Given the application is running, when the window is resized, then all UI elements scale proportionally and remain fully visible. | Yes |
| AC-1.3 | Given the application is in the foreground, when the user alt-tabs away and returns, then no rendering corruption or input lock occurs. | Yes |
| AC-1.4 | Given the application is running, when the user clicks the quit button, then the application closes cleanly within 2 seconds with no hang or orphan process. | Yes |

### REQ-2: Card gameplay

| ID | Criterion | Testable? |
|---|---|---|
| AC-2.1 | Given a new round starts, when the board loads, then all cards are arranged face-down in a rectangular grid. | Yes |
| AC-2.2 | Given a face-down card exists, when the player selects it, then the card flips with a visible animation and reveals food artwork. | Yes |
| AC-2.3 | Given two flipped cards are a matching pair, when the match is evaluated, then both cards stay revealed for the rest of the round. | Yes |
| AC-2.4 | Given two flipped cards are not a matching pair, when the mismatch is evaluated, then both cards flip back to face-down after a delay of at least 0.5 seconds. | Yes |
| AC-2.5 | Given a flip animation is in progress, when the player provides rapid input (clicks or key presses), then that input is ignored and no race condition or double-flip occurs. | Yes |

### REQ-3: Food-themed content

| ID | Criterion | Testable? |
|---|---|---|
| AC-3.1 | Given the assets/images directory contains subfolders, when categories are enumerated, then each subfolder name appears as a category name. | Yes |
| AC-3.2 | Given a category is selected, when the board is populated, then random images from that category's subfolder are loaded onto the cards as matching pairs. | Yes |
| AC-3.3 | Given all shipped image assets, when compared against the asset manifest file, then every image file has a corresponding entry with a source URL and license field. | Yes |
| AC-3.4 | Given any category's images are displayed on cards, when viewed at card size on the game board, then each image is visually distinct and recognizable (no two non-paired images are indistinguishable). | Yes |

### REQ-4: Difficulty levels

| ID | Criterion | Testable? |
|---|---|---|
| AC-4.1 | Given the main menu is displayed, when the player selects a difficulty (easy, normal, or hard), then the game starts with the corresponding board size. | Yes |
| AC-4.2 | Given easy mode is selected, when the board loads, then fewer cards are displayed than in normal mode; given hard mode, then more cards are displayed than in normal mode. | Yes |
| AC-4.3 | Given any difficulty is selected, when a new round starts, then card placement is randomized (repeated starts of the same difficulty do not produce identical layouts). | Yes |

### REQ-5: Score and timer

| ID | Criterion | Testable? |
|---|---|---|
| AC-5.1 | Given a round is in progress, when the player flips two cards (match or mismatch), then the move counter increments by exactly one. | Yes |
| AC-5.2 | Given a round is complete, when the score is calculated, then the result matches the documented score formula (defined in architecture). | Yes |
| AC-5.3 | Given timed mode is active, when the countdown is running, then the displayed timer decreases by one second per real-time second (tolerance +/- 50 ms per tick). | Yes |
| AC-5.4 | Given timed mode is active, when the timer reaches zero, then a fail/retry screen is displayed and no crash or unhandled exception occurs. | Yes |
| AC-5.5 | Given the player has won a round, when the victory screen is displayed, then it shows the correct final score, total moves, and elapsed time. | Yes |

### REQ-6: Save and resume

| ID | Criterion | Testable? |
|---|---|---|
| AC-6.1 | Given a round is in progress, when the player triggers save, then the current game state is persisted to a file. | Yes |
| AC-6.2 | Given a save file exists, when the player launches the application and selects continue, then the round resumes with the correct score, move count, remaining timer value, and matched card positions. | Yes |
| AC-6.3 | Given no save file exists, when the main menu is displayed, then the continue option is disabled or hidden. | Yes |
| AC-6.4 | Given a save file is corrupted (truncated or invalid format), when the application attempts to load it, then an error message is displayed and the application does not crash. | Yes |

### REQ-7: Sound and theme settings

| ID | Criterion | Testable? |
|---|---|---|
| AC-7.1 | Given the settings menu is opened, when the player views the settings, then all configurable options (sound, theme, category, reduced animation) are visible. | Yes |
| AC-7.2 | Given sounds are enabled, when the player flips a card, then a flip sound plays; when a match occurs, then a match sound plays; when a mismatch occurs, then a mismatch sound plays; when the player wins, then a win sound plays; when the player loses, then a lose sound plays. | Yes |
| AC-7.3 | Given the assets/sounds folder, when the game references sound files, then all sound effects are loaded from that folder. | Yes |
| AC-7.4 | Given the player changes the color theme, when the change applies, then the new theme renders immediately without requiring a restart, and all text remains readable. | Yes |
| AC-7.5 | Given the player mutes or unmutes sound, when the application is closed and relaunched, then the mute setting is preserved from the previous session. | Yes |
| AC-7.6 | Given reduced-animation mode is enabled, when the player interacts with cards and menus, then animations are minimized or removed but all interactions remain understandable. | Yes |
| AC-7.7 | Given the application is launched for the first time (no saved settings), when the main menu appears, then the light color theme is active by default. | Yes |
| AC-7.8 | Given the settings menu is opened, when the player views the category option, then all available food categories from assets/images subfolders are listed and selectable. | Yes |
| AC-7.9 | Given the brand color palette is defined, when any theme is rendered, then theme colors use only the specified brand green (G900-G15) and neutrals (N100-N700) values. | Yes |

### REQ-8: Performance

| ID | Criterion | Testable? |
|---|---|---|
| AC-8.1 | Given the application is launched on target hardware, when measuring startup time from process start to main menu visible, then the time is no more than 5 seconds. | Yes |
| AC-8.2 | Given normal gameplay (flipping cards, animations playing), when the frame rate is measured over any 10-second window, then no frame takes longer than 33 ms (sustaining at least 30 FPS). | Yes |
| AC-8.3 | Given the player clicks or presses a key, when the input is processed, then the corresponding visual response begins within 100 ms. | Yes |

### REQ-9: Reliability

| ID | Criterion | Testable? |
|---|---|---|
| AC-9.1 | Given the application is run in a continuous play session, when 30 minutes of repeated rounds elapse, then no crash or unhandled exception occurs. | Yes |
| AC-9.2 | Given save and load are used during normal gameplay, when the save file is inspected after each save, then no data corruption is present (file parses without error). | Yes |
| AC-9.3 | Given any reachable game state, when the player follows the available UI actions, then no dead-end or blocked progression occurs (every screen has a valid exit path). | Yes |
| AC-9.4 | Given the player rapidly restarts rounds (start, quit, start) in quick succession, when state is inspected after each restart, then all counters, timers, and board state are correctly reset. | Yes |

### REQ-10: Usability

| ID | Criterion | Testable? |
|---|---|---|
| AC-10.1 | Given a new player with no prior instructions, when they launch the application, then they can start and complete a round using only the on-screen UI (no external documentation required). | Yes |
| AC-10.2 | Given any active color theme, when text is rendered on its background, then the contrast ratio meets WCAG 2.1 AA minimum (4.5:1 for normal text, 3:1 for large text). | Yes |
| AC-10.3 | Given a round has ended (win or loss), when the result screen is displayed, then it contains an explicit label indicating success or failure and a summary of score, moves, and time. | Yes |

### REQ-11: Accessibility

| ID | Criterion | Testable? |
|---|---|---|
| AC-11.1 | Given the application is running, when the player uses only the keyboard (no mouse), then every game action (navigate menus, select cards, pause, save, quit) is reachable and executable. | Yes |
| AC-11.2 | Given keyboard navigation is active, when focus moves between elements, then a visible focus indicator (outline, highlight, or equivalent) is always displayed on the focused element. | Yes |
| AC-11.3 | Given any active color theme, when all UI elements are audited for color contrast, then all foreground/background combinations meet WCAG 2.1 AA minimum ratios. | Yes |
| AC-11.4 | Given sound is muted and reduced-animation mode is on, when the player plays a full round, then all game state changes are communicated through visual (non-audio, non-animation) cues alone. | Yes |

## Out of Scope

- **Multiplayer or networked play** -- single-player only.
- **Mobile or web platforms** -- desktop Linux and Windows only.
- **Online leaderboards or cloud save** -- all data is local.
- **Custom card artwork upload** -- players use shipped asset categories only.
- **Level editor or custom grid layouts** -- board sizes are fixed per difficulty.
- **Localization / internationalization** -- English only for this release.
- **Gamepad / controller input** -- keyboard and mouse only.
- **In-app asset downloading** -- all assets are bundled with the application.

## Open Questions

- **Q1**: What is the exact score formula? -- The user request references "documented product rules" for the score formula but does not define it. The architecture phase should define a concrete formula (e.g., base points per match, time bonus, move penalty). Until then, AC-5.2 references "the documented score formula" which will be specified in `docs/ARC.md`.
- **Q2**: What are the exact board sizes for each difficulty level? -- The request says easy has fewer cards and hard has more, but does not specify exact grid dimensions. The architecture phase should define concrete grid sizes (e.g., easy: 4x3, normal: 4x4, hard: 6x5). AC-4.1 and AC-4.2 reference "corresponding board size" which will be pinned in `docs/ARC.md`.
- **Q3**: Is timed mode always on, or is it a separate toggle? -- The request mentions "timed mode" with a countdown but does not clarify whether every round is timed or if it is an optional mode. This affects REQ-5. The architecture phase should define how timed mode is activated.
