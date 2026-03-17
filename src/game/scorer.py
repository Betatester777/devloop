# Implements: REQ-4 AC-4.1, AC-4.2, AC-4.3 — Move counter, score formula, countdown timer
# See: ARC §src/game/scorer.py

from __future__ import annotations


class Scorer:
    """Tracks moves, elapsed time, optional countdown, and computes the final score.

    The score formula (from ARC):
        score = max(0, pairs_found × 100 − moves × 5 + remaining_seconds × 2)
    where remaining_seconds = 0 in untimed mode.
    """

    __slots__ = ("moves", "elapsed_seconds", "time_limit", "time_remaining")

    def __init__(self, *, time_limit: float | None = None) -> None:
        self.moves: int = 0
        self.elapsed_seconds: float = 0.0
        self.time_limit: float | None = time_limit
        self.time_remaining: float | None = time_limit

    def record_move(self) -> None:
        """Increment the move counter by exactly 1 (AC-4.1)."""
        self.moves += 1

    def update(self, dt: float) -> bool:
        """Advance elapsed time and countdown.

        Returns ``True`` when the countdown reaches 0 (AC-4.4).
        Always returns ``False`` in untimed mode.
        """
        self.elapsed_seconds += dt

        if self.time_remaining is not None:
            self.time_remaining = max(0.0, self.time_remaining - dt)
            if self.time_remaining <= 0.0:
                return True
        return False

    def compute_score(self, pairs_found: int) -> int:
        """Compute final score using the ARC-defined formula (AC-4.2).

        ``pairs_found × 100 − moves × 5 + remaining_seconds × 2``
        """
        remaining = self.time_remaining if self.time_remaining is not None else 0.0
        raw = pairs_found * 100 - self.moves * 5 + remaining * 2
        return max(0, int(raw))

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "moves": self.moves,
            "elapsed_seconds": self.elapsed_seconds,
            "time_limit": self.time_limit,
            "time_remaining": self.time_remaining,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Scorer:
        scorer = cls(time_limit=data.get("time_limit"))
        scorer.moves = data.get("moves", 0)
        scorer.elapsed_seconds = data.get("elapsed_seconds", 0.0)
        scorer.time_remaining = data.get("time_remaining")
        return scorer
