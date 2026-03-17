# Verifies: AC-4.1 — Move counter increments by exactly 1
# Verifies: AC-4.2 — Score formula matches specification
# Verifies: AC-4.3 — Countdown timer decreases correctly
# Verifies: AC-4.4 — Timer expiry returns True

from __future__ import annotations

from src.game.scorer import Scorer


class TestMoveCounter:
    def test_starts_at_zero(self):
        s = Scorer()
        assert s.moves == 0

    def test_record_move_increments_by_one(self):
        s = Scorer()
        s.record_move()
        assert s.moves == 1

    def test_multiple_moves(self):
        s = Scorer()
        for _ in range(10):
            s.record_move()
        assert s.moves == 10


class TestElapsedTime:
    def test_starts_at_zero(self):
        s = Scorer()
        assert s.elapsed_seconds == 0.0

    def test_update_advances_elapsed(self):
        s = Scorer()
        s.update(1.5)
        assert abs(s.elapsed_seconds - 1.5) < 0.001

    def test_multiple_updates_accumulate(self):
        s = Scorer()
        s.update(0.5)
        s.update(0.5)
        s.update(0.5)
        assert abs(s.elapsed_seconds - 1.5) < 0.001


class TestCountdownTimer:
    def test_untimed_returns_false(self):
        s = Scorer()
        assert s.update(10.0) is False

    def test_untimed_has_no_time_remaining(self):
        s = Scorer()
        assert s.time_remaining is None

    def test_timed_decreases_remaining(self):
        s = Scorer(time_limit=60.0)
        s.update(10.0)
        assert s.time_remaining is not None
        assert abs(s.time_remaining - 50.0) < 0.001

    def test_timed_returns_false_before_expiry(self):
        s = Scorer(time_limit=60.0)
        assert s.update(30.0) is False

    def test_timed_returns_true_on_expiry(self):
        s = Scorer(time_limit=60.0)
        assert s.update(60.1) is True

    def test_time_remaining_never_negative(self):
        s = Scorer(time_limit=10.0)
        s.update(20.0)
        assert s.time_remaining == 0.0

    def test_exact_expiry(self):
        s = Scorer(time_limit=10.0)
        assert s.update(10.0) is True
        assert s.time_remaining == 0.0


class TestScoreFormula:
    def test_basic_untimed(self):
        """score = pairs × 100 − moves × 5 + 0 (untimed)"""
        s = Scorer()
        s.moves = 10
        score = s.compute_score(pairs_found=8)
        # 8 * 100 - 10 * 5 + 0 = 750
        assert score == 750

    def test_with_time_remaining(self):
        """score = pairs × 100 − moves × 5 + remaining × 2"""
        s = Scorer(time_limit=120.0)
        s.update(60.0)
        s.moves = 12
        score = s.compute_score(pairs_found=8)
        # 8 * 100 - 12 * 5 + 60 * 2 = 800 - 60 + 120 = 860
        assert score == 860

    def test_score_never_negative(self):
        s = Scorer()
        s.moves = 1000
        score = s.compute_score(pairs_found=1)
        assert score == 0

    def test_zero_pairs(self):
        s = Scorer()
        s.moves = 5
        score = s.compute_score(pairs_found=0)
        # 0 - 25 = -25 → clamped to 0
        assert score == 0

    def test_perfect_easy_untimed(self):
        """Perfect game: 8 pairs in 8 moves, untimed."""
        s = Scorer()
        s.moves = 8
        score = s.compute_score(pairs_found=8)
        # 800 - 40 = 760
        assert score == 760


class TestSerialization:
    def test_round_trip_untimed(self):
        s = Scorer()
        s.moves = 5
        s.update(30.0)
        d = s.to_dict()
        restored = Scorer.from_dict(d)
        assert restored.moves == 5
        assert abs(restored.elapsed_seconds - 30.0) < 0.001
        assert restored.time_limit is None
        assert restored.time_remaining is None

    def test_round_trip_timed(self):
        s = Scorer(time_limit=120.0)
        s.moves = 10
        s.update(45.0)
        d = s.to_dict()
        restored = Scorer.from_dict(d)
        assert restored.moves == 10
        assert restored.time_limit == 120.0
        assert restored.time_remaining is not None
        assert abs(restored.time_remaining - 75.0) < 0.001
