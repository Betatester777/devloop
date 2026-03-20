# Verifies: AC-2.2, AC-2.4, AC-2.5 — Flip animation timing and input gating
from __future__ import annotations

from src.card_animator import CardAnimator


class TestFlipAnimation:
    def test_start_flip_makes_animating(self) -> None:
        animator = CardAnimator(flip_duration_ms=300)
        assert not animator.is_animating()
        animator.start_flip(0, 0)
        assert animator.is_animating()

    def test_flip_progress_starts_at_zero(self) -> None:
        animator = CardAnimator(flip_duration_ms=300)
        animator.start_flip(0, 0)
        assert animator.flip_progress(0, 0) == 0.0

    def test_flip_progress_midway(self) -> None:
        animator = CardAnimator(flip_duration_ms=300)
        animator.start_flip(0, 0)
        animator.update(150)
        assert abs(animator.flip_progress(0, 0) - 0.5) < 0.01

    def test_flip_completes(self) -> None:
        """AC-2.2: Flip animation runs to completion and emits event."""
        animator = CardAnimator(flip_duration_ms=300)
        animator.start_flip(0, 0)
        events = animator.update(300)
        assert not animator.is_animating()
        assert len(events) == 1
        assert events[0].kind == "flip_complete"

    def test_no_animation_progress_is_one(self) -> None:
        animator = CardAnimator()
        assert animator.flip_progress(0, 0) == 1.0


class TestMismatchDelay:
    def test_mismatch_delay_makes_animating(self) -> None:
        animator = CardAnimator(mismatch_delay_ms=800)
        animator.start_mismatch_delay(0, 0, 0, 1)
        assert animator.is_animating()

    def test_mismatch_delay_minimum_500ms(self) -> None:
        """AC-2.4: Mismatch delay must be at least 500ms."""
        animator = CardAnimator(mismatch_delay_ms=100)
        animator.start_mismatch_delay(0, 0, 0, 1)
        # At 400ms it should still be animating (min is 500ms)
        events = animator.update(400)
        assert animator.is_animating()
        assert len(events) == 0

    def test_mismatch_delay_completes(self) -> None:
        animator = CardAnimator(mismatch_delay_ms=800)
        animator.start_mismatch_delay(0, 0, 0, 1)
        events = animator.update(800)
        assert not animator.is_animating()
        assert len(events) == 1
        assert events[0].kind == "mismatch_delay_complete"


class TestReducedAnimation:
    def test_reduced_mode_instant_flip(self) -> None:
        """ADR-10: Reduced animation makes flips instant."""
        animator = CardAnimator(reduced_animation=True)
        animator.start_flip(0, 0)
        # Even 0ms update should complete the flip
        events = animator.update(0)
        assert len(events) == 1
        assert events[0].kind == "flip_complete"

    def test_reduced_mode_minimum_mismatch_delay(self) -> None:
        """Reduced mode still has minimum 500ms mismatch delay."""
        animator = CardAnimator(reduced_animation=True)
        animator.start_mismatch_delay(0, 0, 0, 1)
        events = animator.update(400)
        assert animator.is_animating()
        events = animator.update(100)
        assert not animator.is_animating()
        assert events[0].kind == "mismatch_delay_complete"
