# Verifies: AC-3.1, AC-3.2, AC-3.3, AC-3.4 — Difficulty levels and board layout
# Verifies: AC-1.1 — Board uses Card state machine
# Requirement: REQ-3 (Difficulty levels), REQ-1 (Card gameplay)

from __future__ import annotations

from src.game.board import BOARD_SIZES, Board, Difficulty
from src.game.card import Card, CardState


class TestDifficulty:
    """AC-3.2: Each difficulty uses a distinct card count (easy < normal < hard)."""

    def test_three_distinct_difficulties(self):
        assert len(Difficulty) == 3

    def test_board_sizes_are_distinct(self):
        sizes = {d: r * c for d, (c, r) in BOARD_SIZES.items()}
        assert sizes[Difficulty.EASY] < sizes[Difficulty.NORMAL] < sizes[Difficulty.HARD]

    def test_easy_size(self):
        cols, rows = BOARD_SIZES[Difficulty.EASY]
        assert (cols, rows) == (4, 4)  # 16 cards, 8 pairs

    def test_normal_size(self):
        cols, rows = BOARD_SIZES[Difficulty.NORMAL]
        assert (cols, rows) == (6, 6)  # 36 cards, 18 pairs

    def test_hard_size(self):
        cols, rows = BOARD_SIZES[Difficulty.HARD]
        assert (cols, rows) == (6, 8)  # 48 cards, 24 pairs

    def test_all_sizes_are_even(self):
        """Board must have an even number of cells for pair matching."""
        for d, (c, r) in BOARD_SIZES.items():
            assert (c * r) % 2 == 0, f"{d.value} has odd cell count"


class TestBoardBuild:
    """AC-3.1: Board built with correct dimensions for each difficulty.
    AC-3.4: Positions differ between builds (randomisation)."""

    def _make_ids(self, n: int) -> list[str]:
        return [f"img_{i:03d}" for i in range(n)]

    def test_build_easy(self):
        ids = self._make_ids(8)
        board = Board.build(Difficulty.EASY, "test_cat", ids)
        assert board.cols == 4
        assert board.rows == 4
        assert len(board.cards) == 16
        assert board.category == "test_cat"
        assert board.difficulty == Difficulty.EASY

    def test_build_normal(self):
        ids = self._make_ids(18)
        board = Board.build(Difficulty.NORMAL, "test_cat", ids)
        assert board.cols == 6
        assert board.rows == 6
        assert len(board.cards) == 36

    def test_build_hard(self):
        ids = self._make_ids(24)
        board = Board.build(Difficulty.HARD, "test_cat", ids)
        assert board.cols == 6
        assert board.rows == 8
        assert len(board.cards) == 48

    def test_each_image_appears_exactly_twice(self):
        ids = self._make_ids(8)
        board = Board.build(Difficulty.EASY, "test_cat", ids)
        from collections import Counter
        counts = Counter(c.image_id for c in board.cards)
        assert all(v == 2 for v in counts.values())
        assert len(counts) == 8

    def test_randomisation_differs_between_builds(self):
        """AC-3.4: Two successive boards should differ in card positions."""
        ids = self._make_ids(8)
        layouts = set()
        for _ in range(20):
            board = Board.build(Difficulty.EASY, "test_cat", ids)
            layout = tuple(c.image_id for c in board.cards)
            layouts.add(layout)
        # With 20 builds, we should see at least 2 distinct layouts
        assert len(layouts) >= 2

    def test_wrong_id_count_raises(self):
        import pytest
        with pytest.raises(ValueError, match="Expected 8"):
            Board.build(Difficulty.EASY, "test_cat", self._make_ids(5))

    def test_randomisation_differs_normal(self):
        """AC-3.4: Two successive Normal boards should differ in card positions."""
        ids = self._make_ids(18)
        layouts: set[tuple[str, ...]] = set()
        for _ in range(20):
            board = Board.build(Difficulty.NORMAL, "test_cat", ids)
            layouts.add(tuple(c.image_id for c in board.cards))
        assert len(layouts) >= 2

    def test_randomisation_differs_hard(self):
        """AC-3.4: Two successive Hard boards should differ in card positions."""
        ids = self._make_ids(24)
        layouts: set[tuple[str, ...]] = set()
        for _ in range(20):
            board = Board.build(Difficulty.HARD, "test_cat", ids)
            layouts.add(tuple(c.image_id for c in board.cards))
        assert len(layouts) >= 2


class TestBoardOperations:
    def _make_board(self) -> Board:
        ids = [f"img_{i:03d}" for i in range(8)]
        return Board.build(Difficulty.EASY, "test_cat", ids)

    def test_card_at(self):
        board = self._make_board()
        card = board.card_at(0, 0)
        assert isinstance(card, Card)
        assert card is board.cards[0]

    def test_card_at_last(self):
        board = self._make_board()
        card = board.card_at(3, 3)
        assert card is board.cards[15]

    def test_all_matched_false_initially(self):
        board = self._make_board()
        assert board.all_matched() is False

    def test_all_matched_true_when_done(self):
        board = self._make_board()
        for c in board.cards:
            c.mark_matched()
        assert board.all_matched() is True


class TestBoardSerialization:
    def test_round_trip(self):
        ids = [f"img_{i:03d}" for i in range(8)]
        board = Board.build(Difficulty.EASY, "test_cat", ids)
        board.cards[0].mark_matched()
        data = board.to_dict()
        restored = Board.from_dict(data)
        assert restored.cols == board.cols
        assert restored.rows == board.rows
        assert restored.category == board.category
        assert restored.difficulty == board.difficulty
        assert len(restored.cards) == len(board.cards)
        assert restored.cards[0].state == CardState.MATCHED
