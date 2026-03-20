# Test Specification

## Test Strategy

Unit tests for each module, executed headlessly with `SDL_VIDEODRIVER=dummy`. Integration tests verify real PNG image loading and manifest validation against actual shipped assets. All tests run via pytest without a visible pygame window. Tests are derived from acceptance criteria in `docs/PRD.md`.

## Test Cases

### REQ-1: Desktop UI and window (43 tests — unchanged from v0.2.0)

| # | Test Case | Traces | Expected Result | Status |
|---|---|---|---|---|
| 1–43 | (See v0.2.0 TST.md for full list) | AC-1.1–AC-1.4 | All pass | Pass |

### REQ-2: Card gameplay (55 tests — unchanged from v0.2.0)

| # | Test Case | Traces | Expected Result | Status |
|---|---|---|---|---|
| 44–72 | (See v0.2.0 TST.md for full list) | AC-2.1–AC-2.5 | All pass | Pass |

### REQ-3: Food-themed content (16 tests — unchanged from v0.3.0)

| # | Test Case | Traces | Expected Result | Status |
|---|---|---|---|---|
| 73 | Real assets directory has expected categories | AC-3.1 | dishes, drinks, etc. present | Pass |
| 74 | Category listing from temp dir returns folder names | AC-3.1 | Returns expected names | Pass |
| 75 | Empty directory returns empty category list | AC-3.1 | Empty list | Pass |
| 76 | Load 10 real PNG images from "dishes" category | AC-3.2 | 10 CardImage instances returned | Pass |
| 77 | Loaded images have unique image_ids | AC-3.2 | All IDs distinct | Pass |
| 78 | Images are scaled to CARD_SIZE | AC-3.4 | (100, 140) surface dimensions | Pass |
| 79 | Random selection produces varied results | AC-3.2 | Two calls return sets (structural) | Pass |
| 80 | AssetError raised when category has insufficient images | AC-3.2 | Error with count message | Pass |
| 81 | AssetError raised when category folder missing | AC-3.2 | Error with "not found" message | Pass |
| 82 | Load from synthetic PNGs in temp directory | AC-3.2, AC-3.4 | 3 images loaded and scaled | Pass |
| 83 | Real asset manifest is complete (all 216 images covered) | AC-3.3 | Empty missing list | Pass |
| 84 | Missing manifest entries detected | AC-3.3 | Returns list of missing stems | Pass |
| 85 | No manifest file treats all images as missing | AC-3.3 | All stems in missing list | Pass |
| 86 | Empty directory returns empty missing list | AC-3.3 | Empty list | Pass |
| 87 | Card back returns surface of CARD_SIZE | AC-3.4 | (100, 140) pygame.Surface | Pass |
| 88 | Card back with custom color | AC-3.4 | Returns pygame.Surface | Pass |

### REQ-4: Difficulty levels (16 new tests)

| # | Test Case | Traces | Expected Result | Status |
|---|---|---|---|---|
| 89 | `TestDifficultyButtons::test_easy_action` | AC-4.1 | Selecting Easy returns `start_game` with `{"difficulty": "easy"}` | Pass |
| 90 | `TestDifficultyButtons::test_normal_action` | AC-4.1 | Selecting Normal returns `start_game` with `{"difficulty": "normal"}` | Pass |
| 91 | `TestDifficultyButtons::test_hard_action` | AC-4.1 | Selecting Hard returns `start_game` with `{"difficulty": "hard"}` | Pass |
| 92 | `TestDifficultyButtons::test_all_three_difficulties_present` | AC-4.1 | Menu focus elements include Easy, Normal, Hard in order | Pass |
| 93 | `TestDifficultyConfigs::test_easy_dimensions` | AC-4.1, AC-4.2 | EASY config is 3 rows x 4 cols | Pass |
| 94 | `TestDifficultyConfigs::test_normal_dimensions` | AC-4.1, AC-4.2 | NORMAL config is 4 rows x 5 cols | Pass |
| 95 | `TestDifficultyConfigs::test_hard_dimensions` | AC-4.1, AC-4.2 | HARD config is 5 rows x 6 cols | Pass |
| 96 | `TestDifficultyConfigs::test_all_have_even_cell_count` | AC-4.2 | Every difficulty has an even cell count (required for pairs) | Pass |
| 97 | `TestDifficultyConfigs::test_timer_seconds_positive` | AC-4.2 | Every difficulty has a positive timer value | Pass |
| 98 | `TestGetDifficulty::test_valid_names` | AC-4.1 | `get_difficulty("easy/normal/hard")` returns correct config | Pass |
| 99 | `TestGetDifficulty::test_invalid_name_raises` | AC-4.1 | `get_difficulty("impossible")` raises `ValueError` | Pass |
| 100 | `TestBoardSizePerDifficulty::test_easy_has_fewer_cards_than_normal` | AC-4.2 | EASY card count (12) < NORMAL card count (20) | Pass |
| 101 | `TestBoardSizePerDifficulty::test_hard_has_more_cards_than_normal` | AC-4.2 | HARD card count (30) > NORMAL card count (20) | Pass |
| 102 | `TestRandomizedPlacement::test_two_shuffles_differ` | AC-4.3 | 10 shuffles produce more than 1 unique layout | Pass |
| 103 | `TestOtherButtons::test_settings_action` (regression) | AC-1.1 | Settings button still works after menu redesign | Pass |
| 104 | `TestDraw::test_draw_does_not_crash` (regression) | AC-1.1 | Menu renders without crash after adding difficulty buttons | Pass |

## Coverage Matrix

| AC ID | Criterion | Test Case(s) | Status |
|---|---|---|---|
| AC-1.1 | Main menu displays without crash | 1–43, 103, 104 | Pass |
| AC-1.2 | UI elements scale proportionally on resize | 14–19, 38, 41 | Pass |
| AC-1.3 | Alt-tab causes no corruption or input lock | 20–25, 31, 41, 43 | Pass |
| AC-1.4 | Quit closes cleanly within 2 seconds | 34, 35, 39, 40, 42 | Pass |
| AC-2.1 | Cards arranged face-down in rectangular grid | 44–46, 64–66, 68–72 | Pass |
| AC-2.2 | Card flips with visible animation revealing artwork | 47–51, 67 | Pass |
| AC-2.3 | Matching pair stays revealed | 52–54, 63 | Pass |
| AC-2.4 | Mismatched pair flips back after >= 0.5s delay | 55–58 | Pass |
| AC-2.5 | Rapid input ignored during animation | 59–62 | Pass |
| AC-3.1 | Subfolders enumerated as category names | 73, 74, 75 | Pass |
| AC-3.2 | Random images from category loaded as pairs | 76, 77, 79, 80, 81, 82 | Pass |
| AC-3.3 | Asset manifest covers every image file | 83, 84, 85, 86 | Pass |
| AC-3.4 | Images visually distinct at card size | 78, 82, 87, 88 | Pass |
| **AC-4.1** | **Difficulty selection starts game with corresponding board size** | **89, 90, 91, 92, 93, 94, 95, 98, 99** | **Pass** |
| **AC-4.2** | **Easy < normal < hard card counts** | **93, 94, 95, 96, 97, 100, 101** | **Pass** |
| **AC-4.3** | **Card placement randomized across repeated starts** | **102** | **Pass** |

## Results

| Metric | Value |
|---|---|
| Total tests | 113 |
| Passed | 113 |
| Failed | 0 |
| Errors | 0 |
| Prior REQ tests (REQ-1 through REQ-3) | 97 (all passing, no regressions) |
| New REQ-4 tests | 16 |
| Lint (ruff) | 0 errors |
| AC coverage | 16/16 AC IDs verified (AC-1.1–1.4, AC-2.1–2.5, AC-3.1–3.4, AC-4.1–4.3) |
| Duration | ~8 seconds |

### Test breakdown by file

| File | Count | Bundles |
|---|---|---|
| `tests/test_assets.py` | 16 | REQ-3 |
| `tests/test_board.py` | 20 | REQ-2 |
| `tests/test_card_animator.py` | 10 | REQ-2 |
| `tests/test_difficulty.py` | 7 | REQ-4 |
| `tests/test_display.py` | 6 | REQ-1 |
| `tests/test_focus_manager.py` | 12 | REQ-1 |
| `tests/test_game_loop.py` | 5 | REQ-1 |
| `tests/test_game_screen.py` | 11 | REQ-2 |
| `tests/test_main_menu.py` | 13 | REQ-1, REQ-4 |
| `tests/test_settings.py` | 6 | REQ-1 |
| `tests/test_theme.py` | 7 | REQ-1 |

## Defects

No defects found.

## Evidence

```
$ pytest tests/ -v
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
collected 113 items
...
============================= 113 passed in 8.08s ==============================

$ ruff check src/ tests/
All checks passed!
```

## Pass Gate

| Criterion | Required | Result |
|---|---|---|
| All tests pass | Yes | 113/113 passed |
| Lint clean | Yes | 0 errors (ruff) |
| Every AC covered by >= 1 test | Yes | AC-4.1 (9 tests), AC-4.2 (7 tests), AC-4.3 (1 test) |
| No regressions in prior bundles | Yes | REQ-1 through REQ-3: 97 tests still passing |
| **Pass gate** | | **PASS** |
