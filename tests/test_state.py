# Verifies: AC-5.1 — GameState serialisation round trip
# Verifies: AC-5.2 — All field values match after deserialisation

from __future__ import annotations

import pytest

from src.game.board import Board, Difficulty
from src.game.scorer import Scorer
from src.game.state import GameState


def _make_board() -> Board:
    """Build a small EASY board with deterministic cards."""
    ids = [f"img_{i:03d}" for i in range(8)]
    return Board.build(Difficulty.EASY, "pizza", ids)


def _make_scorer(*, time_limit: float | None = 180.0) -> Scorer:
    scorer = Scorer(time_limit=time_limit)
    scorer.record_move()
    scorer.record_move()
    scorer.update(5.0)
    return scorer


def _make_state() -> GameState:
    return GameState(
        board=_make_board(),
        scorer=_make_scorer(),
        category="pizza",
        difficulty=Difficulty.EASY,
    )


class TestGameStateRoundTrip:
    """AC-5.1: save → quit → resume restores the game to the exact prior position."""

    def test_round_trip_preserves_all_fields(self):
        original = _make_state()
        data = original.to_dict()
        restored = GameState.from_dict(data)

        assert restored.category == original.category
        assert restored.difficulty == original.difficulty
        assert restored.scorer.moves == original.scorer.moves
        assert restored.scorer.time_limit == original.scorer.time_limit
        assert restored.board.cols == original.board.cols
        assert restored.board.rows == original.board.rows
        assert len(restored.board.cards) == len(original.board.cards)

    def test_card_image_ids_preserved(self):
        original = _make_state()
        data = original.to_dict()
        restored = GameState.from_dict(data)

        orig_ids = [c.image_id for c in original.board.cards]
        rest_ids = [c.image_id for c in restored.board.cards]
        assert rest_ids == orig_ids

    def test_scorer_elapsed_preserved(self):
        original = _make_state()
        data = original.to_dict()
        restored = GameState.from_dict(data)
        assert abs(restored.scorer.elapsed_seconds - original.scorer.elapsed_seconds) < 0.01

    def test_untimed_scorer_round_trip(self):
        state = GameState(
            board=_make_board(),
            scorer=_make_scorer(time_limit=None),
            category="sushi",
            difficulty=Difficulty.EASY,
        )
        restored = GameState.from_dict(state.to_dict())
        assert restored.scorer.time_limit is None
        assert restored.scorer.time_remaining is None


class TestGameStateSchemaVersion:
    def test_to_dict_includes_schema_version(self):
        state = _make_state()
        data = state.to_dict()
        assert "schema_version" in data
        assert data["schema_version"] == 1

    def test_incompatible_version_raises_value_error(self):
        state = _make_state()
        data = state.to_dict()
        data["schema_version"] = 999
        with pytest.raises(ValueError, match="Incompatible save version"):
            GameState.from_dict(data)

    def test_missing_version_raises_value_error(self):
        state = _make_state()
        data = state.to_dict()
        del data["schema_version"]
        with pytest.raises(ValueError, match="Incompatible save version"):
            GameState.from_dict(data)
