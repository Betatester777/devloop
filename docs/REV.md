# Review Package

## Increment Summary

**REQ-4: Difficulty levels** -- Easy/normal/hard modes with varying board sizes, difficulty selection from the main menu, and randomized card placement. This increment replaces the single "New Game" button with three difficulty buttons (Easy 3x4, Normal 4x5, Hard 5x6), wires the selected difficulty through to the game screen, and verifies randomized layouts across repeated starts.

## Changes

| File | Description | Traces |
|---|---|---|
| `src/screens/main_menu.py` | Replaced single "New Game" button with three difficulty buttons ("Easy (3x4)", "Normal (4x5)", "Hard (5x6)"). Each returns `ScreenAction(action="start_game", payload={"difficulty": "<name>"})`. Added "Choose difficulty:" subtitle. Updated focus element list to include all six buttons (3 difficulty + Continue, Settings, Quit). | AC-4.1 |
| `src/game_loop.py` | Updated `_handle_action` to read `difficulty` from `action.payload` instead of always using `self._settings.difficulty`. Persists the selected difficulty to settings. Updated `_create_game_screen` to accept an optional difficulty parameter and look up the corresponding config via `get_difficulty()`. | AC-4.1, AC-4.2 |
| `tests/test_main_menu.py` | Added `TestDifficultyButtons` (4 tests: easy/normal/hard action payloads, all three present). Added `TestBoardSizePerDifficulty` (2 tests: easy < normal, hard > normal). Added `TestRandomizedPlacement` (1 test: 10 shuffles produce more than 1 unique layout). Added regression tests `TestOtherButtons` and `TestDraw`. | AC-4.1, AC-4.2, AC-4.3 |

## Test Results

All tests pass with zero failures and zero lint errors.

| Metric | Value |
|---|---|
| Total tests | 113 |
| Passed | 113 |
| Failed | 0 |
| Lint (ruff) | 0 errors |
| New REQ-4 tests | 16 |
| Prior tests (REQ-1 through REQ-3) | 97 (no regressions) |
| Duration | ~8 seconds |

**AC coverage for REQ-4:**

| AC ID | Criterion | Test count | Status |
|---|---|---|---|
| AC-4.1 | Difficulty selection starts game with corresponding board size | 9 tests | Pass |
| AC-4.2 | Easy < normal < hard card counts | 7 tests | Pass |
| AC-4.3 | Card placement randomized across repeated starts | 1 test | Pass |

## Risks

- **Visual verification not automated.** Grid layout correctness (exact visual alignment of 3x4, 4x5, 5x6 grids) is tested structurally via Board dimensions and card counts but not via pixel-level screenshot tests. Manual demo is recommended.
- **Single randomness test.** AC-4.3 is covered by one test that shuffles 10 times and asserts more than one unique layout. The probability of a false failure is negligible (~1/20!), but it is technically non-deterministic.
- **No timer integration yet.** Difficulty configs include `timer_seconds` values but timer display and countdown are REQ-5 scope and not exercised in this increment.

## Demo Steps

1. Launch the application:
   ```
   python -m src.main
   ```
2. Verify the main menu displays three difficulty buttons: **Easy (3x4)**, **Normal (4x5)**, **Hard (5x6)**, followed by Continue (greyed out), Settings, and Quit.
3. Click **Easy (3x4)** -- verify a 3-column by 4-row grid of face-down cards appears (12 cards total).
4. Press Escape to return to the main menu.
5. Click **Normal (4x5)** -- verify a 4-column by 5-row grid appears (20 cards total).
6. Press Escape to return to the main menu.
7. Click **Hard (5x6)** -- verify a 5-column by 6-row grid appears (30 cards total).
8. Press Escape to return to the main menu.
9. Start the same difficulty twice in a row and confirm the card positions are not identical (randomized placement).
10. Verify keyboard navigation works: use Tab to cycle through buttons and Enter to select.

## Approval Questions

1. **Accept increment?** Does the difficulty selection work correctly, with Easy showing a 3x4 grid, Normal showing a 4x5 grid, and Hard showing a 5x6 grid?
2. **Regressions?** Do existing features (card gameplay, food-themed content, window management) still work as expected?
3. **Ready to proceed?** Shall we move on to REQ-5 (Score and timer)?
