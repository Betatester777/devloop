# Implements: REQ-1 AC-1.2, AC-1.4 — Card state machine with flip animation
# See: ARC §src/game/card.py

from __future__ import annotations

from enum import Enum


class CardState(Enum):
    """States of a card's flip animation lifecycle."""

    FACE_DOWN = "face_down"
    FLIPPING_UP = "flipping_up"
    FACE_UP = "face_up"
    FLIPPING_DOWN = "flipping_down"
    MATCHED = "matched"


# Flip animation completes within 400 ms (AC-1.2).
_FLIP_DURATION = 0.4


class Card:
    """A single memory card with state-machine driven flip animation.

    ``flip_progress`` runs from 0.0 (fully face-down) to 1.0 (fully face-up).
    The ``update(dt)`` method advances the animation each frame.
    """

    __slots__ = ("index", "image_id", "state", "flip_progress")

    def __init__(self, index: int, image_id: str) -> None:
        self.index = index
        self.image_id = image_id
        self.state = CardState.FACE_DOWN
        self.flip_progress: float = 0.0

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def flip_up(self) -> None:
        """Begin flip-up animation (FACE_DOWN → FLIPPING_UP)."""
        if self.state == CardState.FACE_DOWN:
            self.state = CardState.FLIPPING_UP

    def flip_down(self) -> None:
        """Begin flip-down animation (FACE_UP → FLIPPING_DOWN)."""
        if self.state == CardState.FACE_UP:
            self.state = CardState.FLIPPING_DOWN

    def mark_matched(self) -> None:
        """Lock the card as matched (permanently face-up)."""
        self.state = CardState.MATCHED
        self.flip_progress = 1.0

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """Advance flip animation by *dt* seconds."""
        speed = 1.0 / _FLIP_DURATION

        if self.state == CardState.FLIPPING_UP:
            self.flip_progress = min(1.0, self.flip_progress + speed * dt)
            if self.flip_progress >= 1.0:
                self.state = CardState.FACE_UP

        elif self.state == CardState.FLIPPING_DOWN:
            self.flip_progress = max(0.0, self.flip_progress - speed * dt)
            if self.flip_progress <= 0.0:
                self.state = CardState.FACE_DOWN

    def is_animating(self) -> bool:
        """True while a flip animation is in progress."""
        return self.state in (CardState.FLIPPING_UP, CardState.FLIPPING_DOWN)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "image_id": self.image_id,
            "state": self.state.value,
            "flip_progress": self.flip_progress,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Card:
        card = cls(index=data["index"], image_id=data["image_id"])
        saved_state = data.get("state", "face_down")
        # Resumed cards land in FACE_DOWN or MATCHED (no mid-animation resume)
        if saved_state == "matched":
            card.state = CardState.MATCHED
            card.flip_progress = 1.0
        else:
            card.state = CardState.FACE_DOWN
            card.flip_progress = 0.0
        return card
