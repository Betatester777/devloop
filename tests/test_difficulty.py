# Verifies: AC-2.1 — Board dimensions per difficulty level
from __future__ import annotations

import pytest

from src.difficulty import ALL_DIFFICULTIES, EASY, HARD, NORMAL, get_difficulty


class TestDifficultyConfigs:
    def test_easy_dimensions(self) -> None:
        assert EASY.rows == 3
        assert EASY.cols == 4

    def test_normal_dimensions(self) -> None:
        assert NORMAL.rows == 4
        assert NORMAL.cols == 5

    def test_hard_dimensions(self) -> None:
        assert HARD.rows == 5
        assert HARD.cols == 6

    def test_all_have_even_cell_count(self) -> None:
        """Every difficulty must have an even number of cells for pairs."""
        for name, cfg in ALL_DIFFICULTIES.items():
            assert (cfg.rows * cfg.cols) % 2 == 0, f"{name} has odd cell count"

    def test_timer_seconds_positive(self) -> None:
        for name, cfg in ALL_DIFFICULTIES.items():
            assert cfg.timer_seconds > 0, f"{name} has non-positive timer"


class TestGetDifficulty:
    def test_valid_names(self) -> None:
        assert get_difficulty("easy") is EASY
        assert get_difficulty("normal") is NORMAL
        assert get_difficulty("hard") is HARD

    def test_invalid_name_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown difficulty"):
            get_difficulty("impossible")
