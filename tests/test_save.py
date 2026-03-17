# Verifies: AC-5.1 — SaveManager save/load round trip
# Verifies: AC-5.3 — has_save() returns correct state
# Verifies: AC-5.4 — Corrupted/absent save raises SaveError

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.game.board import Board, Difficulty
from src.game.scorer import Scorer
from src.game.state import GameState
from src.save import SaveError, SaveManager


def _make_state() -> GameState:
    ids = [f"img_{i:03d}" for i in range(8)]
    board = Board.build(Difficulty.EASY, "pizza", ids)
    scorer = Scorer(time_limit=180.0)
    scorer.record_move()
    scorer.update(3.5)
    return GameState(
        board=board,
        scorer=scorer,
        category="pizza",
        difficulty=Difficulty.EASY,
    )


@pytest.fixture()
def save_path(tmp_path: Path) -> Path:
    return tmp_path / "save.json"


@pytest.fixture()
def mgr(save_path: Path) -> SaveManager:
    return SaveManager(save_path=save_path)


class TestSaveManagerSaveLoad:
    """AC-5.1: save/load round trip produces identical GameState."""

    def test_save_creates_file(self, mgr: SaveManager, save_path: Path):
        state = _make_state()
        mgr.save(state)
        assert save_path.is_file()

    def test_load_returns_equivalent_state(self, mgr: SaveManager):
        original = _make_state()
        mgr.save(original)
        restored = mgr.load()
        assert restored.category == original.category
        assert restored.difficulty == original.difficulty
        assert restored.scorer.moves == original.scorer.moves
        assert len(restored.board.cards) == len(original.board.cards)

    def test_save_file_is_valid_json(self, mgr: SaveManager, save_path: Path):
        mgr.save(_make_state())
        data = json.loads(save_path.read_text("utf-8"))
        assert "schema_version" in data

    def test_overwrite_existing_save(self, mgr: SaveManager):
        state1 = _make_state()
        state1.scorer.record_move()
        mgr.save(state1)
        state2 = _make_state()
        mgr.save(state2)
        restored = mgr.load()
        assert restored.scorer.moves == state2.scorer.moves


class TestSaveManagerHasSave:
    """AC-5.3: has_save reflects file presence."""

    def test_no_save_initially(self, mgr: SaveManager):
        assert mgr.has_save() is False

    def test_has_save_after_save(self, mgr: SaveManager):
        mgr.save(_make_state())
        assert mgr.has_save() is True

    def test_has_save_after_delete(self, mgr: SaveManager):
        mgr.save(_make_state())
        mgr.delete()
        assert mgr.has_save() is False


class TestSaveManagerDelete:
    def test_delete_removes_file(self, mgr: SaveManager, save_path: Path):
        mgr.save(_make_state())
        mgr.delete()
        assert not save_path.exists()

    def test_delete_when_no_file_is_noop(self, mgr: SaveManager):
        mgr.delete()  # Should not raise


class TestSaveManagerErrors:
    """AC-5.4: corrupted or absent saves produce human-readable errors."""

    def test_load_absent_file_raises_save_error(self, mgr: SaveManager):
        with pytest.raises(SaveError, match="No save file found"):
            mgr.load()

    def test_load_corrupted_json_raises_save_error(
        self, mgr: SaveManager, save_path: Path
    ):
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text("{not valid json", encoding="utf-8")
        with pytest.raises(SaveError, match="corrupted"):
            mgr.load()

    def test_load_incompatible_version_raises_save_error(
        self, mgr: SaveManager, save_path: Path
    ):
        state = _make_state()
        data = state.to_dict()
        data["schema_version"] = 999
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(SaveError, match="incompatible"):
            mgr.load()

    def test_load_missing_keys_raises_save_error(
        self, mgr: SaveManager, save_path: Path
    ):
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text('{"schema_version": 1}', encoding="utf-8")
        with pytest.raises(SaveError, match="incompatible"):
            mgr.load()
