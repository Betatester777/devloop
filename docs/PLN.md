# Feature Bundle Plan

## Active Bundle

**REQ-4: Difficulty levels** (Bundle 4 of 11)

Easy/normal/hard modes with varying board sizes, difficulty selection from main menu, randomized placement.

## Tasks

| # | Task | Traces | Dependencies | Status |
|---|---|---|---|---|
| 1 | **Add difficulty selection buttons to MainMenuScreen** — Replace the single "New Game" button with three difficulty buttons: "Easy (3×4)", "Normal (4×5)", "Hard (5×6)". Each returns `ScreenAction(action="start_game", payload={"difficulty": "<name>"})`. Keep Continue, Settings, Quit buttons below. Update focus elements accordingly. | AC-4.1 | -- | Done |
| 2 | **Update GameLoop to read difficulty from action payload** — Modify `_handle_action` and `_create_game_screen` to accept the difficulty from `ScreenAction.payload["difficulty"]` instead of always reading from `self._settings.difficulty`. Also persist the selected difficulty to `self._settings.difficulty` so it's remembered. | AC-4.1, AC-4.2 | 1 | Done |
| 3 | **Write/update tests for REQ-4** — Add tests to `tests/test_main_menu.py` verifying difficulty button presence and correct action payloads. Add tests confirming board sizes differ per difficulty (easy < normal < hard). Verify randomized placement by checking two consecutive boards don't have identical layouts. | AC-4.1, AC-4.2, AC-4.3 | 1, 2 | Done |

## Dependencies

- **Python 3.12+**, **pygame**, **pytest**, **ruff** installed.
- **REQ-3 complete**: asset loader, board, game screen all implemented.
- **`src/difficulty.py`** already defines EASY (3×4), NORMAL (4×5), HARD (5×6) configs.

## Definition of Ready

- `docs/ARC.md` §14 (difficulty) and ADR-2 (Board Sizes) cover all REQ-4 requirements.
- `docs/PRD.md` acceptance criteria AC-4.1 through AC-4.3 are finalized.
- REQ-3 is complete and passing.

## Definition of Done

- All 3 tasks are complete with status Done.
- `pytest tests/` passes with zero failures (REQ-1 through REQ-4 tests).
- `ruff check src/ tests/` reports zero errors.
- The main menu shows Easy, Normal, Hard buttons; each starts a game with the correct board size.
- Every acceptance criterion (AC-4.1 through AC-4.3) is covered by at least one passing test.

## Validation Commands

```bash
# Run REQ-4 tests
pytest tests/test_main_menu.py tests/test_difficulty.py -v

# Run all tests (no regressions)
pytest tests/ -v

# Lint
ruff check src/ tests/

# Visual verification
python -m src.main
# → Main menu shows Easy (3×4), Normal (4×5), Hard (5×6) buttons
# → Click Easy → 3×4 grid; click Hard → 5×6 grid
```

## Validated Start Command

```bash
python -m src.main
```
