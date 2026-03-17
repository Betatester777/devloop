# Implements: REQ-5 AC-5.1, AC-5.2 — Aggregate game state for save/resume
# See: ARC §src/game/state.py

from __future__ import annotations

from dataclasses import dataclass

from src.game.board import Board, Difficulty
from src.game.scorer import Scorer

_SCHEMA_VERSION = 1


@dataclass
class GameState:
    """Full snapshot of a round in progress, suitable for serialisation."""

    board: Board
    scorer: Scorer
    category: str
    difficulty: Difficulty

    def to_dict(self) -> dict:
        return {
            "schema_version": _SCHEMA_VERSION,
            "board": self.board.to_dict(),
            "scorer": self.scorer.to_dict(),
            "category": self.category,
            "difficulty": self.difficulty.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> GameState:
        version = data.get("schema_version", 0)
        if version != _SCHEMA_VERSION:
            raise ValueError(
                f"Incompatible save version: expected {_SCHEMA_VERSION}, got {version}"
            )
        return cls(
            board=Board.from_dict(data["board"]),
            scorer=Scorer.from_dict(data["scorer"]),
            category=data["category"],
            difficulty=Difficulty(data["difficulty"]),
        )
