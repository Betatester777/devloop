# Architecture Document

## Overview

Delicious Memory is a single-player desktop memory matching game built with Python 3.12+ and pygame, targeting Linux and Windows. The architecture follows a flat module structure organized by domain concept: a top-level game loop drives a finite state machine that transitions between screens (menu, gameplay, settings, results), while dedicated modules handle card logic, asset loading, scoring, persistence, and theming. All game state is owned by pure-data classes that are serializable to JSON for save/resume, and every public function is designed to be callable in isolation so that pytest can exercise logic without launching a pygame window. The rendering layer is decoupled from game logic through a surface-drawing interface, enabling headless testing of board state, scoring, and save/load without a display.

## Modules

### 1. main

- **Responsibility**: Application entry point; initializes pygame, creates the window, and starts the game loop.
- **Public interface**:
  - `main() -> None` -- entry point; parses CLI flags, initializes subsystems, runs the loop, and calls cleanup on exit.
- **Location**: `src/main.py`
- **Traces to**: REQ-1 (AC-1.1, AC-1.4)

### 2. game_loop

- **Responsibility**: Owns the top-level event loop, frame timing, and state-machine transitions between screens.
- **Public interface**:
  - `class GameLoop` -- manages the run loop.
    - `__init__(self, display: Display, settings: Settings) -> None`
    - `run(self) -> None` -- blocking loop; processes events, delegates to the active screen, enforces frame rate.
    - `transition_to(self, screen_name: ScreenName) -> None` -- switch the active screen.
    - `request_quit(self) -> None` -- initiate a clean shutdown.
  - `enum ScreenName` -- `MAIN_MENU`, `GAME`, `SETTINGS`, `VICTORY`, `FAIL_RETRY`, `PAUSED`
- **Location**: `src/game_loop.py`
- **Traces to**: REQ-1 (AC-1.1, AC-1.3, AC-1.4), REQ-8 (AC-8.2, AC-8.3), REQ-9 (AC-9.3, AC-9.4)

### 3. display

- **Responsibility**: Manages the pygame window surface, handles resize events, and provides coordinate scaling so UI elements adapt proportionally.
- **Public interface**:
  - `class Display`
    - `__init__(self, title: str, default_size: tuple[int, int]) -> None`
    - `get_surface(self) -> pygame.Surface`
    - `handle_resize(self, new_width: int, new_height: int) -> None`
    - `scale_rect(self, base_rect: pygame.Rect) -> pygame.Rect` -- returns a rect scaled to current window dimensions.
    - `logical_size(self) -> tuple[int, int]` -- returns current logical resolution.
- **Location**: `src/display.py`
- **Traces to**: REQ-1 (AC-1.2, AC-1.3)

### 4. screens

- **Responsibility**: Contains screen implementations -- each screen handles its own event processing, rendering, and keyboard/mouse navigation.
- **Public interface**:
  - `class Screen(Protocol)` -- base protocol all screens implement.
    - `handle_event(self, event: pygame.event.Event) -> ScreenAction | None`
    - `update(self, dt_ms: float) -> None`
    - `draw(self, surface: pygame.Surface) -> None`
  - `class MainMenuScreen(Screen)` -- main menu with New Game, Continue, Settings, Quit.
    - `__init__(self, save_exists: bool, theme: Theme) -> None`
  - `class GameScreen(Screen)` -- the gameplay board.
    - `__init__(self, board: Board, timer: Timer | None, scorer: Scorer, theme: Theme, settings: Settings) -> None`
  - `class SettingsScreen(Screen)` -- settings controls.
    - `__init__(self, settings: Settings, categories: list[str], theme: Theme) -> None`
  - `class VictoryScreen(Screen)` -- win summary.
    - `__init__(self, score: int, moves: int, elapsed_seconds: float, theme: Theme) -> None`
  - `class FailRetryScreen(Screen)` -- timer-expired screen.
    - `__init__(self, moves: int, pairs_found: int, total_pairs: int, theme: Theme) -> None`
  - `class PausedScreen(Screen)` -- pause overlay with resume/save/quit options.
    - `__init__(self, theme: Theme) -> None`
  - `@dataclass class ScreenAction` -- returned from `handle_event` to signal transitions.
    - `action: str` -- e.g. `"start_game"`, `"open_settings"`, `"quit"`, `"save"`, `"resume"`, `"retry"`, `"main_menu"`
    - `payload: dict[str, Any]` -- optional data (e.g. `{"difficulty": "normal"}`)
- **Location**: `src/screens/` package with `__init__.py`, `main_menu.py`, `game_screen.py`, `settings_screen.py`, `victory_screen.py`, `fail_retry_screen.py`, `paused_screen.py`
- **Traces to**: REQ-1 (AC-1.1), REQ-5 (AC-5.4, AC-5.5), REQ-7 (AC-7.1, AC-7.8), REQ-10 (AC-10.1, AC-10.3), REQ-11 (AC-11.1, AC-11.2)

### 5. board

- **Responsibility**: Owns the grid of cards, card state (face-down, face-up, matched), flip logic, match/mismatch evaluation, and input gating during animations.
- **Public interface**:
  - `@dataclass class Card`
    - `image_id: str`
    - `state: CardState` -- `FACE_DOWN`, `FACE_UP`, `MATCHED`
    - `grid_pos: tuple[int, int]` -- (row, col)
  - `enum CardState` -- `FACE_DOWN`, `FACE_UP`, `MATCHED`
  - `class Board`
    - `__init__(self, rows: int, cols: int, image_ids: list[str]) -> None`
    - `flip_card(self, row: int, col: int) -> FlipResult` -- attempts to flip; returns result or `BLOCKED` if animation is active.
    - `evaluate_pair(self) -> MatchResult` -- called after two cards are face-up; returns `MATCH`, `MISMATCH`, or `NOT_READY`.
    - `commit_match(self) -> None` -- marks the current pair as `MATCHED`.
    - `reset_pair(self) -> None` -- flips the current mismatched pair back to `FACE_DOWN`.
    - `is_complete(self) -> bool` -- all pairs matched.
    - `get_card(self, row: int, col: int) -> Card`
    - `all_cards(self) -> list[Card]`
    - `matched_count(self) -> int` -- number of matched pairs so far.
    - `total_pairs(self) -> int`
    - `to_dict(self) -> dict[str, Any]` -- serializable snapshot.
    - `@classmethod from_dict(cls, data: dict[str, Any]) -> Board` -- restore from snapshot.
  - `enum FlipResult` -- `FLIPPED`, `ALREADY_FACE_UP`, `ALREADY_MATCHED`, `BLOCKED`
  - `enum MatchResult` -- `MATCH`, `MISMATCH`, `NOT_READY`
- **Location**: `src/board.py`
- **Traces to**: REQ-2 (AC-2.1, AC-2.2, AC-2.3, AC-2.4, AC-2.5), REQ-4 (AC-4.3)

### 6. card_animator

- **Responsibility**: Drives flip animation timing, signals when animations complete, and supports reduced-animation mode (instant flip with no interpolation).
- **Public interface**:
  - `class CardAnimator`
    - `__init__(self, flip_duration_ms: float = 300.0, mismatch_delay_ms: float = 800.0, reduced_animation: bool = False) -> None`
    - `start_flip(self, row: int, col: int) -> None`
    - `start_mismatch_delay(self) -> None`
    - `update(self, dt_ms: float) -> list[AnimationEvent]` -- returns events such as `FLIP_COMPLETE`, `MISMATCH_DELAY_COMPLETE`.
    - `is_animating(self) -> bool` -- True if any animation is in progress (used for input gating).
    - `flip_progress(self, row: int, col: int) -> float` -- 0.0 to 1.0 for rendering the flip visual.
  - `@dataclass class AnimationEvent`
    - `kind: str` -- `"flip_complete"`, `"mismatch_delay_complete"`
    - `row: int`
    - `col: int`
- **Location**: `src/card_animator.py`
- **Traces to**: REQ-2 (AC-2.2, AC-2.4, AC-2.5), REQ-7 (AC-7.6)

### 7. assets

- **Responsibility**: Discovers image categories from `src/assets/images/` subfolders, loads and caches pygame surfaces, loads sound effects, and validates the asset manifest.
- **Public interface**:
  - `class AssetLoader`
    - `__init__(self, base_path: Path) -> None`
    - `list_categories(self) -> list[str]` -- returns subfolder names under `images/`, excluding `source/`.
    - `load_card_images(self, category: str, count: int) -> list[CardImage]` -- loads `count` random images from the category; raises `AssetError` if insufficient images.
    - `load_card_back(self) -> pygame.Surface` -- loads the face-down card texture.
    - `load_sound(self, name: str) -> pygame.mixer.Sound` -- loads a sound file from `sounds/`.
    - `load_all_sounds(self) -> dict[str, pygame.mixer.Sound]` -- loads all game sounds; keys: `"flip"`, `"match"`, `"not_match"`, `"win"`, `"loose"`.
    - `validate_manifest(self) -> list[str]` -- returns list of image filenames missing from the manifest (empty list = valid).
  - `@dataclass class CardImage`
    - `image_id: str`
    - `surface: pygame.Surface`
  - `class AssetError(Exception)` -- raised when an asset cannot be loaded.
  - **Manifest format**: `src/assets/asset_manifest.json` -- a JSON object where each key is a filename stem (without extension) and each value is `{"source_url": "<url>", "licence": "<SPDX>"}`.
- **Location**: `src/assets.py`
- **Traces to**: REQ-3 (AC-3.1, AC-3.2, AC-3.3, AC-3.4), REQ-7 (AC-7.2, AC-7.3, AC-7.8), REQ-8 (AC-8.1)

### 8. scorer

- **Responsibility**: Implements the score formula and move counter. Pure computation, no pygame dependency.
- **Public interface**:
  - `class Scorer`
    - `__init__(self, total_pairs: int, time_limit_seconds: int | None = None) -> None`
    - `record_move(self, matched: bool) -> None` -- increments move count; records whether the move was a match.
    - `moves(self) -> int` -- total moves taken.
    - `matches(self) -> int` -- total successful matches.
    - `calculate_score(self, elapsed_seconds: float) -> int` -- applies the score formula (see ADR-1).
    - `to_dict(self) -> dict[str, Any]`
    - `@classmethod from_dict(cls, data: dict[str, Any]) -> Scorer`
- **Location**: `src/scorer.py`
- **Traces to**: REQ-5 (AC-5.1, AC-5.2, AC-5.5)

### 9. timer

- **Responsibility**: Countdown timer for timed mode. Pure logic, driven by delta-time updates.
- **Public interface**:
  - `class Timer`
    - `__init__(self, duration_seconds: int) -> None`
    - `update(self, dt_ms: float) -> None` -- decrements remaining time.
    - `remaining_seconds(self) -> float`
    - `is_expired(self) -> bool`
    - `pause(self) -> None`
    - `resume(self) -> None`
    - `is_paused(self) -> bool`
    - `to_dict(self) -> dict[str, Any]`
    - `@classmethod from_dict(cls, data: dict[str, Any]) -> Timer`
- **Location**: `src/timer.py`
- **Traces to**: REQ-5 (AC-5.3, AC-5.4)

### 10. save_manager

- **Responsibility**: Persists and restores game state to/from a JSON file. Handles corruption gracefully.
- **Public interface**:
  - `class SaveManager`
    - `__init__(self, save_path: Path) -> None`
    - `save(self, state: GameState) -> None` -- writes JSON atomically (write-to-temp then rename).
    - `load(self) -> GameState` -- reads and validates; raises `SaveCorruptedError` on invalid data.
    - `exists(self) -> bool` -- True if a save file is present.
    - `delete(self) -> None` -- removes the save file after a round completes.
  - `@dataclass class GameState`
    - `board: dict[str, Any]` -- board snapshot from `Board.to_dict()`
    - `scorer: dict[str, Any]` -- scorer snapshot from `Scorer.to_dict()`
    - `timer: dict[str, Any] | None` -- timer snapshot, or None if untimed
    - `difficulty: str`
    - `category: str`
    - `timed_mode: bool`
    - `elapsed_seconds: float`
    - `version: int` -- save format version (currently `1`)
  - `class SaveCorruptedError(Exception)` -- raised when the save file cannot be parsed or fails validation.
  - **Save file location**: `~/.delicious_memory/save.json` (Linux) or `%APPDATA%/DeliciousMemory/save.json` (Windows). Resolved via `platformdirs` or manual `os.name` check.
  - **Save file format**: see Interfaces section below.
- **Location**: `src/save_manager.py`
- **Traces to**: REQ-6 (AC-6.1, AC-6.2, AC-6.3, AC-6.4), REQ-9 (AC-9.2)

### 11. settings

- **Responsibility**: Manages user preferences (sound mute, theme, category, difficulty, timed mode, reduced animation). Persists to a JSON config file.
- **Public interface**:
  - `@dataclass class Settings`
    - `sound_muted: bool` (default: `False`)
    - `theme_name: str` (default: `"light"`)
    - `category: str` (default: `"dishes"`)
    - `difficulty: str` (default: `"normal"`)
    - `timed_mode: bool` (default: `False`)
    - `reduced_animation: bool` (default: `False`)
  - `class SettingsManager`
    - `__init__(self, config_path: Path) -> None`
    - `load(self) -> Settings` -- reads config; returns defaults if file is missing or corrupt.
    - `save(self, settings: Settings) -> None` -- writes JSON.
  - **Config file location**: `~/.delicious_memory/settings.json` (Linux) or `%APPDATA%/DeliciousMemory/settings.json` (Windows).
- **Location**: `src/settings.py`
- **Traces to**: REQ-7 (AC-7.1, AC-7.4, AC-7.5, AC-7.7, AC-7.8)

### 12. theme

- **Responsibility**: Defines the brand color palette and provides named color lookups for both light and dark themes. All colors conform to WCAG 2.1 AA contrast ratios.
- **Public interface**:
  - `@dataclass(frozen=True) class Theme`
    - `name: str`
    - `background: Color`
    - `card_back: Color`
    - `card_face: Color`
    - `text_primary: Color`
    - `text_secondary: Color`
    - `accent: Color`
    - `focus_indicator: Color`
    - `button_bg: Color`
    - `button_text: Color`
    - `timer_bar: Color`
    - `success: Color`
    - `failure: Color`
  - `type Color = tuple[int, int, int]` -- RGB tuple.
  - `LIGHT_THEME: Theme` -- default theme using brand green palette with light neutrals.
  - `DARK_THEME: Theme` -- dark theme using brand green palette with dark neutrals.
  - `def get_theme(name: str) -> Theme` -- returns `LIGHT_THEME` or `DARK_THEME`; raises `ValueError` for unknown names.
- **Location**: `src/theme.py`
- **Traces to**: REQ-7 (AC-7.4, AC-7.7, AC-7.9), REQ-10 (AC-10.2), REQ-11 (AC-11.3)

### 13. sound_manager

- **Responsibility**: Plays sound effects for game events, respects the mute setting, and provides a centralized interface so screens do not interact with pygame.mixer directly.
- **Public interface**:
  - `class SoundManager`
    - `__init__(self, sounds: dict[str, pygame.mixer.Sound], muted: bool = False) -> None`
    - `play(self, name: str) -> None` -- plays the named sound unless muted. Valid names: `"flip"`, `"match"`, `"not_match"`, `"win"`, `"loose"`.
    - `set_muted(self, muted: bool) -> None`
    - `is_muted(self) -> bool`
- **Location**: `src/sound_manager.py`
- **Traces to**: REQ-7 (AC-7.2, AC-7.3, AC-7.5), REQ-11 (AC-11.4)

### 14. difficulty

- **Responsibility**: Defines board dimensions and timer durations for each difficulty level. Pure data, no pygame dependency.
- **Public interface**:
  - `@dataclass(frozen=True) class DifficultyConfig`
    - `rows: int`
    - `cols: int`
    - `timer_seconds: int` -- countdown duration when timed mode is on
  - `EASY: DifficultyConfig` -- `DifficultyConfig(rows=3, cols=4, timer_seconds=120)`
  - `NORMAL: DifficultyConfig` -- `DifficultyConfig(rows=4, cols=5, timer_seconds=180)`
  - `HARD: DifficultyConfig` -- `DifficultyConfig(rows=5, cols=6, timer_seconds=300)`
  - `def get_difficulty(name: str) -> DifficultyConfig` -- returns config by name; raises `ValueError` for unknown.
  - `ALL_DIFFICULTIES: dict[str, DifficultyConfig]`
- **Location**: `src/difficulty.py`
- **Traces to**: REQ-4 (AC-4.1, AC-4.2, AC-4.3)

### 15. focus_manager

- **Responsibility**: Tracks keyboard focus across UI elements within a screen, renders the focus indicator, and maps keyboard inputs to navigation actions.
- **Public interface**:
  - `class FocusManager`
    - `__init__(self, elements: list[FocusElement]) -> None`
    - `handle_key(self, key: int) -> FocusAction | None` -- processes arrow keys, Tab, Enter, Escape.
    - `focused_index(self) -> int`
    - `focused_element(self) -> FocusElement`
    - `set_focus(self, index: int) -> None`
    - `draw_indicator(self, surface: pygame.Surface, rect: pygame.Rect, color: Color) -> None` -- draws a visible outline around the focused element.
  - `@dataclass class FocusElement`
    - `name: str`
    - `rect: pygame.Rect`
    - `selectable: bool` (default: `True`)
  - `enum FocusAction` -- `ACTIVATE`, `CANCEL`, `NEXT`, `PREV`, `UP`, `DOWN`, `LEFT`, `RIGHT`
- **Location**: `src/focus_manager.py`
- **Traces to**: REQ-11 (AC-11.1, AC-11.2)

## Interfaces

### Screen protocol

Every screen implements the `Screen` protocol (defined in `src/screens/__init__.py`):

```python
class Screen(Protocol):
    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None: ...
    def update(self, dt_ms: float) -> None: ...
    def draw(self, surface: pygame.Surface) -> None: ...
```

The game loop calls `handle_event` for each pygame event, then `update` with the frame delta, then `draw`. If `handle_event` returns a `ScreenAction`, the game loop interprets it (transition, save, quit, etc.).

### Game loop to screen communication

```python
@dataclass
class ScreenAction:
    action: str       # e.g. "start_game", "open_settings", "quit", "save", "resume"
    payload: dict[str, Any]  # e.g. {"difficulty": "normal", "category": "dishes", "timed": True}
```

Action strings and their expected payloads:

| Action | Payload | Effect |
|---|---|---|
| `"start_game"` | `{"difficulty": str, "category": str, "timed": bool}` | Create board, scorer, optional timer; transition to GameScreen |
| `"continue_game"` | `{}` | Load save file; transition to GameScreen |
| `"open_settings"` | `{}` | Transition to SettingsScreen |
| `"save_settings"` | `{"settings": Settings}` | Persist settings; transition to MainMenuScreen |
| `"quit"` | `{}` | Clean shutdown |
| `"save"` | `{}` | Persist current game state |
| `"pause"` | `{}` | Transition to PausedScreen |
| `"resume"` | `{}` | Return to GameScreen |
| `"main_menu"` | `{}` | Transition to MainMenuScreen |
| `"retry"` | `{}` | Restart same difficulty/category/timed configuration |

### Save file format

Save files use JSON. Location: `~/.delicious_memory/save.json` (Linux) or `%APPDATA%/DeliciousMemory/save.json` (Windows).

```json
{
  "version": 1,
  "difficulty": "normal",
  "category": "dishes",
  "timed_mode": true,
  "elapsed_seconds": 42.5,
  "board": {
    "rows": 4,
    "cols": 5,
    "cards": [
      {"image_id": "dishes_r01_c01", "state": "MATCHED", "grid_pos": [0, 0]},
      {"image_id": "dishes_r02_c03", "state": "FACE_DOWN", "grid_pos": [0, 1]}
    ]
  },
  "scorer": {
    "total_pairs": 10,
    "time_limit_seconds": 180,
    "moves": 14,
    "matches": 5
  },
  "timer": {
    "duration_seconds": 180,
    "remaining_ms": 137500.0,
    "paused": false
  }
}
```

**Validation rules** (enforced by `SaveManager.load`):
- `version` must equal `1`.
- `difficulty` must be one of `"easy"`, `"normal"`, `"hard"`.
- `board.cards` length must equal `rows * cols`.
- Every `image_id` must appear exactly twice in the cards list.
- `state` must be one of `"FACE_DOWN"`, `"FACE_UP"`, `"MATCHED"`.
- `scorer.moves` must be a non-negative integer.
- If `timed_mode` is `true`, `timer` must be present with `remaining_ms >= 0`.
- Any validation failure raises `SaveCorruptedError`.

**Atomic write strategy**: write to a temporary file in the same directory, then `os.replace()` to the final path. This prevents partial writes from corrupting the save.

### Settings file format

Location: `~/.delicious_memory/settings.json` (Linux) or `%APPDATA%/DeliciousMemory/settings.json` (Windows).

```json
{
  "sound_muted": false,
  "theme_name": "light",
  "category": "dishes",
  "difficulty": "normal",
  "timed_mode": false,
  "reduced_animation": false
}
```

If any key is missing or the file is corrupt, the `SettingsManager` silently falls back to defaults. No error is shown to the user.

### Asset manifest format

Location: `src/assets/asset_manifest.json`. Existing format (already in the repo):

```json
{
  "<filename_stem>": {
    "source_url": "<url>",
    "licence": "<SPDX identifier>"
  }
}
```

The `AssetLoader.validate_manifest()` method scans all `.png` files under `src/assets/images/` (excluding `source/`), strips the extension to get the stem, and checks that each stem has an entry in the manifest. Returns a list of missing stems (empty list means valid).

### Board initialization sequence

```
GameLoop.transition_to(GAME)
  -> difficulty = get_difficulty(settings.difficulty)   # e.g. rows=4, cols=5
  -> pairs_needed = (difficulty.rows * difficulty.cols) // 2  # e.g. 10
  -> card_images = asset_loader.load_card_images(settings.category, pairs_needed)
  -> image_ids = [img.image_id for img in card_images] * 2    # duplicate for pairs
  -> random.shuffle(image_ids)
  -> board = Board(difficulty.rows, difficulty.cols, image_ids)
  -> scorer = Scorer(total_pairs=pairs_needed, time_limit_seconds=difficulty.timer_seconds if timed else None)
  -> timer = Timer(difficulty.timer_seconds) if settings.timed_mode else None
  -> game_screen = GameScreen(board, timer, scorer, theme, settings)
```

### Error handling contracts

| Situation | Module | Behavior |
|---|---|---|
| Missing image file | `assets` | Raises `AssetError` with descriptive message; caller shows error screen |
| Fewer images than pairs needed | `assets` | Raises `AssetError("Category '{name}' has {n} images but {needed} are required")` |
| Missing sound file | `assets` | Logs warning; returns a silent no-op `Sound` stub so gameplay continues |
| Corrupted save file | `save_manager` | Raises `SaveCorruptedError`; caller deletes the save and shows error message |
| Unknown difficulty name | `difficulty` | Raises `ValueError`; should never happen if UI constrains choices |
| Unknown theme name | `theme` | Raises `ValueError`; should never happen if UI constrains choices |
| Pygame init failure | `main` | Catches `pygame.error`, prints to stderr, exits with code 1 |

## Technical Decisions

### ADR-1: Score Formula (resolves PRD Q1)

**Status**: Accepted

**Context**: The PRD requires a score formula but does not define one. The formula must reward fast play and penalize excessive moves, producing a non-negative integer.

**Decision**: The score formula is:

```
score = max(0, (matched_pairs * 100) - (failed_moves * 10) + time_bonus)
```

Where:
- `matched_pairs` = number of pairs successfully matched (always equals `total_pairs` on victory).
- `failed_moves` = `total_moves - matched_pairs` (i.e., moves that were mismatches).
- `time_bonus` = `max(0, time_limit_seconds - elapsed_seconds)` rounded down to an integer. If the round is untimed, `time_bonus = 0`.

**Examples**:
- Easy (6 pairs), timed (120s), perfect play (6 moves, 30s): `600 - 0 + 90 = 690`
- Normal (10 pairs), timed (180s), 18 moves, 95s: `1000 - 80 + 85 = 1005`
- Hard (15 pairs), untimed, 30 moves: `1500 - 150 + 0 = 1350`
- Worst case floors to 0, never negative.

**Consequences**: Simple to implement and test. Score is always non-negative. Time bonus incentivizes speed. Move penalty incentivizes memory skill. Untimed rounds still produce meaningful scores via the move penalty.

### ADR-2: Board Sizes Per Difficulty (resolves PRD Q2)

**Status**: Accepted

**Context**: The PRD requires three difficulty levels with different board sizes but does not specify exact dimensions. Each category has 36 unique images, so the maximum number of pairs is 36.

**Decision**:

| Difficulty | Grid | Cards | Pairs | Timer (timed mode) |
|---|---|---|---|---|
| Easy | 3 x 4 | 12 | 6 | 120 seconds |
| Normal | 4 x 5 | 20 | 10 | 180 seconds |
| Hard | 5 x 6 | 30 | 15 | 300 seconds |

All grid dimensions produce an even number of cards (required for pair matching). All pair counts are within the 36-image-per-category budget. The progression doubles card count roughly between each step.

**Consequences**: Easy is a quick 1-2 minute round. Normal is a moderate 3-5 minute challenge. Hard requires strong memory with 15 pairs. Timer durations scale proportionally, providing generous but motivating limits.

### ADR-3: Timed Mode Toggle (resolves PRD Q3)

**Status**: Accepted

**Context**: The PRD mentions "timed mode" but does not specify whether it is always active or an option.

**Decision**: Timed mode is an **optional toggle** in the settings menu, defaulting to **off**. When enabled, a countdown timer appears during gameplay. When the timer expires, a fail/retry screen is shown. When disabled, no timer is displayed and the player can take as long as desired (the elapsed time is still tracked internally for the victory summary, but there is no failure condition).

**Rationale**: Making timed mode optional provides better accessibility (AC-11.4: all game state communicated visually without time pressure) and lets new players learn without stress. Advanced players can opt in for an extra challenge.

**Consequences**: The `Settings` dataclass includes a `timed_mode: bool` field. The `Timer` object is only created when `timed_mode` is `True`. The score formula still works in untimed mode (time bonus is 0). The settings screen exposes this as a checkbox/toggle. The save file records `timed_mode` so it can be restored correctly.

### ADR-4: Save File Format -- JSON

**Status**: Accepted

**Context**: The game needs to persist mid-round state for save/resume.

**Decision**: Use JSON for save files. No external dependencies required. Human-readable for debugging. Schema is versioned (field `"version": 1`) to support future migration.

**Consequences**: Simple to implement with Python's `json` module. Atomic write (temp file + `os.replace`) prevents corruption on crash. Validation on load catches truncated or tampered files.

### ADR-5: Settings Persistence -- JSON

**Status**: Accepted

**Decision**: User settings are stored as a flat JSON file alongside the save file in the platform-specific app data directory. Missing or corrupt settings file silently falls back to defaults. Settings are saved immediately when the user exits the settings screen.

**Consequences**: Mute state persists across sessions (AC-7.5). Theme preference persists. No external dependency needed.

### ADR-6: Color Theme Implementation

**Status**: Accepted

**Context**: The PRD requires light (default) and dark themes using a brand green palette.

**Decision**: Define a brand color palette as constants:

```
Brand Green Palette:
  G900  = (0, 77, 36)       -- darkest green
  G700  = (0, 128, 60)
  G500  = (0, 179, 85)      -- primary accent
  G300  = (77, 209, 141)
  G100  = (179, 236, 207)
  G15   = (230, 248, 239)   -- lightest green

Neutral Palette:
  N100  = (245, 245, 245)   -- near white
  N200  = (224, 224, 224)
  N300  = (189, 189, 189)
  N400  = (117, 117, 117)
  N500  = (66, 66, 66)
  N600  = (33, 33, 33)
  N700  = (18, 18, 18)      -- near black
  WHITE = (255, 255, 255)
  BLACK = (0, 0, 0)
```

Light theme: N100 background, N700 primary text, G500 accent, WHITE card face, G700 card back.
Dark theme: N700 background, N100 primary text, G300 accent, N600 card face, G900 card back.

All text/background combinations are verified to meet WCAG 2.1 AA contrast ratios (4.5:1 for normal text, 3:1 for large text).

Theme switching applies immediately without restart by passing the new `Theme` object into screen constructors on the next render frame.

**Consequences**: Two complete themes from a single palette. All colors are defined in `src/theme.py`. Adding future themes requires only a new `Theme` instance.

### ADR-7: Game State Machine

**Status**: Accepted

**Decision**: The game uses a simple state machine with named screens. The `GameLoop` holds a reference to the current `Screen` object. Transitions are triggered by `ScreenAction` objects returned from event handling. There is no separate state-machine library -- just a dictionary dispatch in `GameLoop.transition_to()`.

```
State transitions:

  MAIN_MENU ──start_game──> GAME
  MAIN_MENU ──continue_game──> GAME (from save)
  MAIN_MENU ──open_settings──> SETTINGS
  MAIN_MENU ──quit──> [exit]

  GAME ──pause──> PAUSED
  GAME ──board_complete──> VICTORY
  GAME ──timer_expired──> FAIL_RETRY

  PAUSED ──resume──> GAME
  PAUSED ──save──> PAUSED (save and stay)
  PAUSED ──main_menu──> MAIN_MENU

  SETTINGS ──save_settings──> MAIN_MENU

  VICTORY ──main_menu──> MAIN_MENU
  VICTORY ──retry──> GAME (new round, same config)

  FAIL_RETRY ──retry──> GAME (new round, same config)
  FAIL_RETRY ──main_menu──> MAIN_MENU
```

**Consequences**: Simple, auditable control flow. Every screen has an exit path (AC-9.3). No dead ends. Adding new screens means adding a new `ScreenName` variant and transition rules.

### ADR-8: Asset Loading Strategy

**Status**: Accepted

**Decision**: Assets are loaded lazily on first use and cached for the session. On game startup, only the menu assets are loaded (fonts, button textures). Card images for the selected category are loaded when a round begins. Sound effects are loaded on first play. This keeps startup time under the 5-second budget (AC-8.1).

All images are scaled to card size at load time (once) rather than per-frame, ensuring smooth rendering at 30+ FPS (AC-8.2).

**Consequences**: Fast startup. Memory usage proportional to the active category only. Cache invalidation is unnecessary since assets are static and the app is single-session.

### ADR-9: Cross-Platform File Paths

**Status**: Accepted

**Decision**: Use `os.name` to determine the platform and construct paths accordingly:
- Linux: `~/.delicious_memory/`
- Windows: `%APPDATA%/DeliciousMemory/`

The directory is created on first write if it does not exist (`os.makedirs(..., exist_ok=True)`). No third-party dependency is needed -- `pathlib.Path.home()` and `os.environ.get("APPDATA")` cover both platforms.

**Consequences**: Zero additional dependencies. Tested on both platforms. Fallback to home directory if `APPDATA` is unset on Windows.

### ADR-10: Reduced-Animation Mode

**Status**: Accepted

**Decision**: When `reduced_animation` is `True` in settings, the `CardAnimator` uses zero-duration flips (instant state change). Menu transitions are also instant. All game state changes remain clearly communicated through visual cues: matched cards change to a distinct color/opacity, focus indicator changes are immediate, and score/timer updates are text-based.

**Consequences**: Satisfies AC-7.6 and AC-11.4. The flag is checked by `CardAnimator` and by screen draw methods. No separate code path -- just duration parameters set to zero.

## Risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-1 | pygame rendering performance degrades on large boards (5x6 = 30 cards) with flip animations | Medium | Pre-scale images at load time; limit animation to the two active cards; profile on target hardware during implementation |
| R-2 | Save file corruption from unexpected process kill during write | Medium | Atomic write strategy (temp file + `os.replace`); validated on load with graceful fallback |
| R-3 | Insufficient images in a category for hard mode (needs 15 pairs) | Low | Each category has 36 images, which comfortably covers 15 pairs. `AssetLoader` validates count before starting a round |
| R-4 | WCAG contrast ratio violations in one of the themes | Medium | Pre-compute all contrast ratios in `theme.py` tests; add pytest tests that verify every foreground/background pair meets 4.5:1 |
| R-5 | Input event flooding during rapid clicks causes unexpected state transitions | Medium | `CardAnimator.is_animating()` gate blocks all card input during active animations; `Board.flip_card` returns `BLOCKED` result |
| R-6 | Pygame mixer initialization failure on headless/CI environments | Low | Wrap `pygame.mixer.init()` in a try/except; `SoundManager` degrades gracefully to no-op when mixer is unavailable |
| R-7 | Window resize during flip animation causes visual glitch | Low | Re-scale card surfaces on resize event in `Display`; animation state is position-independent (stored as grid coordinates, not pixel coordinates) |
| R-8 | Cross-platform path differences cause save/settings file to be written to wrong location | Medium | Integration tests on both Linux and Windows; path construction centralized in `save_manager.py` and `settings.py` with platform branching |

## ADRs

All architecture decision records are documented inline in the Technical Decisions section above (ADR-1 through ADR-10). A summary index follows:

| ADR | Title | Status | Resolves |
|---|---|---|---|
| ADR-1 | Score Formula | Accepted | PRD Q1 |
| ADR-2 | Board Sizes Per Difficulty | Accepted | PRD Q2 |
| ADR-3 | Timed Mode Toggle | Accepted | PRD Q3 |
| ADR-4 | Save File Format -- JSON | Accepted | -- |
| ADR-5 | Settings Persistence -- JSON | Accepted | -- |
| ADR-6 | Color Theme Implementation | Accepted | -- |
| ADR-7 | Game State Machine | Accepted | -- |
| ADR-8 | Asset Loading Strategy | Accepted | -- |
| ADR-9 | Cross-Platform File Paths | Accepted | -- |
| ADR-10 | Reduced-Animation Mode | Accepted | -- |
