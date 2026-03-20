# Implements: REQ-2 AC-2.1, AC-2.3, AC-2.4, AC-2.5 — Card grid, flip logic, match evaluation
# See: ARC §5 (board)
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class CardState(Enum):
    FACE_DOWN = auto()
    FACE_UP = auto()
    MATCHED = auto()


class FlipResult(Enum):
    FLIPPED = auto()
    ALREADY_FACE_UP = auto()
    ALREADY_MATCHED = auto()
    BLOCKED = auto()


class MatchResult(Enum):
    MATCH = auto()
    MISMATCH = auto()
    NOT_READY = auto()


@dataclass
class Card:
    image_id: str
    state: CardState
    grid_pos: tuple[int, int]


class Board:
    """Rectangular grid of cards with flip, match, and input-gating logic."""

    def __init__(self, rows: int, cols: int, image_ids: list[str]) -> None:
        if len(image_ids) != rows * cols:
            raise ValueError(
                f"Expected {rows * cols} image_ids, got {len(image_ids)}"
            )
        self._rows = rows
        self._cols = cols
        self._animation_lock = False
        self._cards: list[list[Card]] = []
        idx = 0
        for r in range(rows):
            row: list[Card] = []
            for c in range(cols):
                row.append(Card(
                    image_id=image_ids[idx],
                    state=CardState.FACE_DOWN,
                    grid_pos=(r, c),
                ))
                idx += 1
            self._cards.append(row)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    # ------------------------------------------------------------------
    # Animation lock (input gating for AC-2.5)
    # ------------------------------------------------------------------

    def set_animation_lock(self) -> None:
        self._animation_lock = True

    def clear_animation_lock(self) -> None:
        self._animation_lock = False

    @property
    def animation_locked(self) -> bool:
        return self._animation_lock

    # ------------------------------------------------------------------
    # Card access
    # ------------------------------------------------------------------

    def get_card(self, row: int, col: int) -> Card:
        return self._cards[row][col]

    def all_cards(self) -> list[Card]:
        return [card for row in self._cards for card in row]

    # ------------------------------------------------------------------
    # Flip logic
    # ------------------------------------------------------------------

    def flip_card(self, row: int, col: int) -> FlipResult:
        if self._animation_lock:
            return FlipResult.BLOCKED
        card = self._cards[row][col]
        if card.state is CardState.MATCHED:
            return FlipResult.ALREADY_MATCHED
        if card.state is CardState.FACE_UP:
            return FlipResult.ALREADY_FACE_UP
        # Don't allow flipping a third card while two are already face-up
        face_up = self._face_up_cards()
        if len(face_up) >= 2:
            return FlipResult.BLOCKED
        card.state = CardState.FACE_UP
        return FlipResult.FLIPPED

    # ------------------------------------------------------------------
    # Pair evaluation
    # ------------------------------------------------------------------

    def evaluate_pair(self) -> MatchResult:
        face_up = self._face_up_cards()
        if len(face_up) != 2:
            return MatchResult.NOT_READY
        a, b = face_up
        if a.image_id == b.image_id:
            return MatchResult.MATCH
        return MatchResult.MISMATCH

    def commit_match(self) -> None:
        for card in self._face_up_cards():
            card.state = CardState.MATCHED

    def reset_pair(self) -> None:
        for card in self._face_up_cards():
            card.state = CardState.FACE_DOWN

    # ------------------------------------------------------------------
    # Completion
    # ------------------------------------------------------------------

    def is_complete(self) -> bool:
        return all(c.state is CardState.MATCHED for c in self.all_cards())

    def matched_count(self) -> int:
        return sum(1 for c in self.all_cards() if c.state is CardState.MATCHED) // 2

    def total_pairs(self) -> int:
        return (self._rows * self._cols) // 2

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows": self._rows,
            "cols": self._cols,
            "cards": [
                {
                    "image_id": c.image_id,
                    "state": c.state.name,
                    "grid_pos": list(c.grid_pos),
                }
                for c in self.all_cards()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Board:
        rows = data["rows"]
        cols = data["cols"]
        cards_data = data["cards"]
        image_ids = [c["image_id"] for c in cards_data]
        board = cls(rows, cols, image_ids)
        for card_data in cards_data:
            r, c = card_data["grid_pos"]
            board._cards[r][c].state = CardState[card_data["state"]]
        return board

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _face_up_cards(self) -> list[Card]:
        return [c for c in self.all_cards() if c.state is CardState.FACE_UP]
