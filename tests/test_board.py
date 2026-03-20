# Verifies: AC-2.1, AC-2.3, AC-2.4, AC-2.5 — Card grid, flip, match, input gating
from __future__ import annotations

import pytest

from src.board import Board, CardState, FlipResult, MatchResult


def _make_board(rows: int = 2, cols: int = 2) -> Board:
    """Create a small board with known image IDs for testing."""
    # 2x2 board: two pairs (A, A, B, B)
    ids = ["A", "A", "B", "B"]
    if rows * cols != len(ids):
        ids = []
        num_pairs = (rows * cols) // 2
        for i in range(num_pairs):
            ids.extend([f"img_{i}", f"img_{i}"])
    return Board(rows, cols, ids)


class TestBoardCreation:
    def test_dimensions(self) -> None:
        board = _make_board()
        assert board.rows == 2
        assert board.cols == 2

    def test_all_cards_face_down(self) -> None:
        board = _make_board()
        for card in board.all_cards():
            assert card.state is CardState.FACE_DOWN

    def test_wrong_image_count_raises(self) -> None:
        with pytest.raises(ValueError, match="Expected 4"):
            Board(2, 2, ["A", "B", "C"])

    def test_total_pairs(self) -> None:
        board = _make_board()
        assert board.total_pairs() == 2


class TestFlipCard:
    def test_flip_face_down_card(self) -> None:
        board = _make_board()
        result = board.flip_card(0, 0)
        assert result is FlipResult.FLIPPED
        assert board.get_card(0, 0).state is CardState.FACE_UP

    def test_flip_already_face_up(self) -> None:
        board = _make_board()
        board.flip_card(0, 0)
        result = board.flip_card(0, 0)
        assert result is FlipResult.ALREADY_FACE_UP

    def test_flip_matched_card(self) -> None:
        board = _make_board()
        # Manually set a card to MATCHED
        board.get_card(0, 0).state = CardState.MATCHED
        result = board.flip_card(0, 0)
        assert result is FlipResult.ALREADY_MATCHED

    def test_third_flip_blocked(self) -> None:
        """Cannot flip a third card while two are already face-up."""
        board = _make_board()
        board.flip_card(0, 0)
        board.flip_card(0, 1)
        result = board.flip_card(1, 0)
        assert result is FlipResult.BLOCKED


class TestAnimationLock:
    """AC-2.5: Input gating during animations."""

    def test_flip_blocked_during_animation(self) -> None:
        board = _make_board()
        board.set_animation_lock()
        result = board.flip_card(0, 0)
        assert result is FlipResult.BLOCKED

    def test_flip_allowed_after_lock_cleared(self) -> None:
        board = _make_board()
        board.set_animation_lock()
        board.clear_animation_lock()
        result = board.flip_card(0, 0)
        assert result is FlipResult.FLIPPED

    def test_animation_locked_property(self) -> None:
        board = _make_board()
        assert not board.animation_locked
        board.set_animation_lock()
        assert board.animation_locked


class TestPairEvaluation:
    def test_not_ready_with_zero_face_up(self) -> None:
        board = _make_board()
        assert board.evaluate_pair() is MatchResult.NOT_READY

    def test_not_ready_with_one_face_up(self) -> None:
        board = _make_board()
        board.flip_card(0, 0)
        assert board.evaluate_pair() is MatchResult.NOT_READY

    def test_match(self) -> None:
        """AC-2.3: Two cards with same image_id are a match."""
        # Build a board where (0,0) and (0,1) are the same image
        board = Board(2, 2, ["X", "X", "Y", "Y"])
        board.flip_card(0, 0)
        board.flip_card(0, 1)
        assert board.evaluate_pair() is MatchResult.MATCH

    def test_mismatch(self) -> None:
        """AC-2.4: Two cards with different image_id are a mismatch."""
        board = Board(2, 2, ["X", "Y", "X", "Y"])
        board.flip_card(0, 0)  # X
        board.flip_card(0, 1)  # Y
        assert board.evaluate_pair() is MatchResult.MISMATCH


class TestCommitAndReset:
    def test_commit_match(self) -> None:
        """AC-2.3: Matched cards stay revealed."""
        board = Board(2, 2, ["X", "X", "Y", "Y"])
        board.flip_card(0, 0)
        board.flip_card(0, 1)
        board.commit_match()
        assert board.get_card(0, 0).state is CardState.MATCHED
        assert board.get_card(0, 1).state is CardState.MATCHED
        assert board.matched_count() == 1

    def test_reset_pair(self) -> None:
        """AC-2.4: Mismatched pair flips back face-down."""
        board = Board(2, 2, ["X", "Y", "X", "Y"])
        board.flip_card(0, 0)
        board.flip_card(0, 1)
        board.reset_pair()
        assert board.get_card(0, 0).state is CardState.FACE_DOWN
        assert board.get_card(0, 1).state is CardState.FACE_DOWN


class TestCompletion:
    def test_not_complete_initially(self) -> None:
        board = _make_board()
        assert not board.is_complete()

    def test_complete_when_all_matched(self) -> None:
        board = Board(2, 2, ["X", "X", "Y", "Y"])
        # Match first pair
        board.flip_card(0, 0)
        board.flip_card(0, 1)
        board.commit_match()
        # Match second pair
        board.flip_card(1, 0)
        board.flip_card(1, 1)
        board.commit_match()
        assert board.is_complete()
        assert board.matched_count() == 2


class TestSerialization:
    def test_round_trip(self) -> None:
        board = Board(2, 2, ["X", "X", "Y", "Y"])
        board.flip_card(0, 0)
        board.flip_card(0, 1)
        board.commit_match()

        data = board.to_dict()
        restored = Board.from_dict(data)

        assert restored.rows == 2
        assert restored.cols == 2
        assert restored.get_card(0, 0).state is CardState.MATCHED
        assert restored.get_card(1, 0).state is CardState.FACE_DOWN
