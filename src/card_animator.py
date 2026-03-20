# Implements: REQ-2 AC-2.2, AC-2.4, AC-2.5 — Flip animation timing and input gating
# See: ARC §6 (card_animator), ADR-10 (Reduced-Animation Mode)
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AnimationEvent:
    """Emitted by CardAnimator.update when an animation completes."""

    kind: str  # "flip_complete" or "mismatch_delay_complete"
    row: int
    col: int


class CardAnimator:
    """Drives flip animation timing and mismatch delay."""

    def __init__(
        self,
        flip_duration_ms: float = 300.0,
        mismatch_delay_ms: float = 800.0,
        reduced_animation: bool = False,
    ) -> None:
        self._flip_duration = 0.0 if reduced_animation else flip_duration_ms
        self._mismatch_delay = max(mismatch_delay_ms, 500.0)  # AC-2.4: >= 500ms
        if reduced_animation:
            self._mismatch_delay = 500.0  # minimum even in reduced mode

        # Active flip animations: {(row, col): elapsed_ms}
        self._flips: dict[tuple[int, int], float] = {}
        # Mismatch delay: (elapsed_ms, row1, col1, row2, col2) or None
        self._mismatch: tuple[float, int, int, int, int] | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_flip(self, row: int, col: int) -> None:
        """Begin a flip animation for the card at (row, col)."""
        self._flips[(row, col)] = 0.0

    def start_mismatch_delay(self, row1: int, col1: int, row2: int, col2: int) -> None:
        """Begin the mismatch pause before flipping cards back."""
        self._mismatch = (0.0, row1, col1, row2, col2)

    def update(self, dt_ms: float) -> list[AnimationEvent]:
        """Advance all timers. Returns events for completed animations."""
        events: list[AnimationEvent] = []

        # Advance flip animations
        completed_flips: list[tuple[int, int]] = []
        for key in self._flips:
            self._flips[key] += dt_ms
            if self._flips[key] >= self._flip_duration:
                completed_flips.append(key)
        for key in completed_flips:
            del self._flips[key]
            events.append(AnimationEvent(kind="flip_complete", row=key[0], col=key[1]))

        # Advance mismatch delay
        if self._mismatch is not None:
            elapsed, r1, c1, r2, c2 = self._mismatch
            elapsed += dt_ms
            if elapsed >= self._mismatch_delay:
                self._mismatch = None
                events.append(AnimationEvent(kind="mismatch_delay_complete", row=r1, col=c1))
            else:
                self._mismatch = (elapsed, r1, c1, r2, c2)

        return events

    def is_animating(self) -> bool:
        """True if any flip animation or mismatch delay is active."""
        return bool(self._flips) or self._mismatch is not None

    def flip_progress(self, row: int, col: int) -> float:
        """Return 0.0–1.0 progress for the flip at (row, col). 1.0 if not animating."""
        key = (row, col)
        if key not in self._flips or self._flip_duration == 0:
            return 1.0
        return min(self._flips[key] / self._flip_duration, 1.0)
