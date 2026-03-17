# Implements: REQ-1 AC-1.3, AC-1.4 — Match/mismatch detection and input lock
# See: ARC §src/game/match_engine.py

from __future__ import annotations

from enum import Enum

from src.game.card import Card, CardState


class GameEvent(Enum):
    """Events emitted by the match engine."""

    MATCH = "match"
    MISMATCH = "mismatch"
    BOARD_CLEAR = "board_clear"


# How long mismatched cards stay face-up before flipping back (AC-1.3: 1–2 s).
_MISMATCH_DELAY = 1.5


class MatchEngine:
    """Tracks flipped cards, detects matches, and enforces input lock.

    ``input_locked`` is True while a flip animation is running or while
    waiting for mismatched cards to flip back (AC-1.4).
    """

    def __init__(self) -> None:
        self._first: Card | None = None
        self._second: Card | None = None
        self._mismatch_timer: float = 0.0
        self.input_locked: bool = False

    def flip(self, card: Card) -> GameEvent | None:
        """Attempt to flip *card* face-up.

        Returns a ``GameEvent`` if the flip immediately triggers one,
        otherwise ``None``.  Input is silently ignored when locked (AC-1.4).
        """
        if self.input_locked:
            return None

        # Ignore cards that are already face-up, matched, or animating
        if card.state != CardState.FACE_DOWN:
            return None

        card.flip_up()

        if self._first is None:
            self._first = card
            return None

        # Second card flipped — lock input until animations complete
        self._second = card
        self.input_locked = True
        return None

    def update(self, dt: float, cards: list[Card]) -> GameEvent | None:
        """Advance animation state and detect match/mismatch.

        Call once per frame.  Returns a ``GameEvent`` when a match or
        mismatch resolves, or ``BOARD_CLEAR`` when all cards are matched.
        """
        # Advance all card animations
        for c in cards:
            c.update(dt)

        # Waiting for mismatch timer to expire
        if self._mismatch_timer > 0:
            self._mismatch_timer -= dt
            if self._mismatch_timer <= 0:
                # Flip mismatched cards back down
                if self._first is not None:
                    self._first.flip_down()
                if self._second is not None:
                    self._second.flip_down()
                self._first = None
                self._second = None
                self._mismatch_timer = 0.0
                self.input_locked = False
                return GameEvent.MISMATCH
            return None

        # Both cards have been selected — wait for animations to finish
        if self._first is not None and self._second is not None:
            if self._first.is_animating() or self._second.is_animating():
                return None  # Still animating

            # Both face-up — check match
            if self._first.image_id == self._second.image_id:
                self._first.mark_matched()
                self._second.mark_matched()
                self._first = None
                self._second = None
                self.input_locked = False

                # Check if the entire board is cleared
                if all(c.state == CardState.MATCHED for c in cards):
                    return GameEvent.BOARD_CLEAR
                return GameEvent.MATCH
            else:
                # Mismatch — start delay timer (AC-1.3: 1–2 s)
                self._mismatch_timer = _MISMATCH_DELAY
                return None

        # Nothing pending
        if self._first is None and self._second is None:
            self.input_locked = False

        return None
