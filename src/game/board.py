# Implements: REQ-3 AC-3.1, AC-3.2, AC-3.4 — Board layout and difficulty levels
# Implements: REQ-1 AC-1.1 — Grid layout with Card state machine
# See: ARC §src/game/board.py

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from src.game.card import Card, CardState


class Difficulty(Enum):
    """Game difficulty levels, each maps to a distinct board size."""

    EASY = "easy"  # 4×4 = 16 cards, 8 pairs
    NORMAL = "normal"  # 6×6 = 36 cards, 18 pairs
    HARD = "hard"  # 6×8 = 48 cards, 24 pairs


BOARD_SIZES: dict[Difficulty, tuple[int, int]] = {
    Difficulty.EASY: (4, 4),
    Difficulty.NORMAL: (6, 6),
    Difficulty.HARD: (6, 8),
}


@dataclass
class Board:
    """Grid of cards built from a chosen category and difficulty."""

    cols: int
    rows: int
    cards: list[Card] = field(default_factory=list)
    category: str = ""
    difficulty: Difficulty = Difficulty.EASY

    def card_at(self, col: int, row: int) -> Card:
        """Return the card at grid position (col, row)."""
        return self.cards[row * self.cols + col]

    def all_matched(self) -> bool:
        """True when every card on the board has been matched."""
        return all(c.state == CardState.MATCHED for c in self.cards)

    @staticmethod
    def build(
        difficulty: Difficulty, category: str, image_ids: list[str]
    ) -> Board:
        """Create a new shuffled board for the given difficulty.

        *image_ids* must contain exactly ``n_pairs`` unique IDs where
        ``n_pairs = (cols * rows) // 2``.  Each ID is duplicated to form
        pairs and the resulting list is shuffled randomly.
        """
        cols, rows = BOARD_SIZES[difficulty]
        n_pairs = (cols * rows) // 2

        if len(image_ids) != n_pairs:
            raise ValueError(
                f"Expected {n_pairs} unique image IDs for {difficulty.value}, "
                f"got {len(image_ids)}"
            )

        # Duplicate each ID to create pairs and shuffle
        paired = image_ids * 2
        random.shuffle(paired)

        cards = [Card(index=i, image_id=img_id) for i, img_id in enumerate(paired)]
        return Board(
            cols=cols,
            rows=rows,
            cards=cards,
            category=category,
            difficulty=difficulty,
        )

    def to_dict(self) -> dict:
        return {
            "cols": self.cols,
            "rows": self.rows,
            "cards": [c.to_dict() for c in self.cards],
            "category": self.category,
            "difficulty": self.difficulty.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Board:
        return cls(
            cols=data["cols"],
            rows=data["rows"],
            cards=[Card.from_dict(c) for c in data["cards"]],
            category=data["category"],
            difficulty=Difficulty(data["difficulty"]),
        )
