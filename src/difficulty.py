# Implements: REQ-2 AC-2.1 — Board dimensions per difficulty level
# See: ARC §14 (difficulty), ADR-2 (Board Sizes Per Difficulty)
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DifficultyConfig:
    """Board dimensions and timer duration for a difficulty level."""

    rows: int
    cols: int
    timer_seconds: int


EASY = DifficultyConfig(rows=3, cols=4, timer_seconds=120)
NORMAL = DifficultyConfig(rows=4, cols=5, timer_seconds=180)
HARD = DifficultyConfig(rows=5, cols=6, timer_seconds=300)

ALL_DIFFICULTIES: dict[str, DifficultyConfig] = {
    "easy": EASY,
    "normal": NORMAL,
    "hard": HARD,
}


def get_difficulty(name: str) -> DifficultyConfig:
    """Return a difficulty config by name. Raises ``ValueError`` for unknown names."""
    try:
        return ALL_DIFFICULTIES[name]
    except KeyError:
        valid = ", ".join(sorted(ALL_DIFFICULTIES))
        raise ValueError(
            f"Unknown difficulty '{name}'. Valid difficulties: {valid}"
        ) from None
