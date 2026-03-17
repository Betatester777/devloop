# Verifies: AC-1.3 — Match/mismatch logic with correct event emission
# Verifies: AC-1.4 — Input lock during animation and mismatch delay

from __future__ import annotations

from src.game.card import Card, CardState, _FLIP_DURATION
from src.game.match_engine import GameEvent, MatchEngine, _MISMATCH_DELAY


def _make_pair(image_id: str = "pizza_01") -> list[Card]:
    """Create two cards with the same image_id (a matching pair)."""
    return [Card(index=0, image_id=image_id), Card(index=1, image_id=image_id)]


def _make_mismatch() -> list[Card]:
    """Create two cards with different image_ids."""
    return [Card(index=0, image_id="pizza_01"), Card(index=1, image_id="cake_01")]


class TestMatchDetection:
    def test_match_emits_match_event(self):
        # Include extra unmatched cards so BOARD_CLEAR is not triggered
        cards = _make_pair() + [Card(index=2, image_id="extra_01"), Card(index=3, image_id="extra_01")]
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        # Advance past flip animation
        event = engine.update(_FLIP_DURATION + 0.01, cards)
        assert event == GameEvent.MATCH

    def test_matched_cards_state(self):
        cards = _make_pair()
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        engine.update(_FLIP_DURATION + 0.01, cards)
        assert cards[0].state == CardState.MATCHED
        assert cards[1].state == CardState.MATCHED

    def test_mismatch_emits_mismatch_event_after_delay(self):
        cards = _make_mismatch()
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        # Wait for flip animation to complete
        engine.update(_FLIP_DURATION + 0.01, cards)
        # Now mismatch timer starts, wait for it to expire
        event = engine.update(_MISMATCH_DELAY + 0.01, cards)
        assert event == GameEvent.MISMATCH

    def test_mismatch_flips_cards_back(self):
        cards = _make_mismatch()
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        engine.update(_FLIP_DURATION + 0.01, cards)
        engine.update(_MISMATCH_DELAY + 0.01, cards)
        # Cards should now be flipping down
        assert cards[0].state in (CardState.FLIPPING_DOWN, CardState.FACE_DOWN)
        assert cards[1].state in (CardState.FLIPPING_DOWN, CardState.FACE_DOWN)


class TestInputLock:
    def test_locked_during_second_flip_animation(self):
        cards = _make_pair()
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        assert engine.input_locked is True

    def test_unlocked_after_match(self):
        cards = _make_pair()
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        engine.update(_FLIP_DURATION + 0.01, cards)
        assert engine.input_locked is False

    def test_locked_during_mismatch_delay(self):
        cards = _make_mismatch()
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        engine.update(_FLIP_DURATION + 0.01, cards)
        # Now in mismatch delay — should still be locked
        engine.update(0.1, cards)
        assert engine.input_locked is True

    def test_unlocked_after_mismatch_resolved(self):
        cards = _make_mismatch()
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        engine.update(_FLIP_DURATION + 0.01, cards)
        engine.update(_MISMATCH_DELAY + 0.01, cards)
        assert engine.input_locked is False

    def test_flip_ignored_when_locked(self):
        cards = [
            Card(index=0, image_id="a"),
            Card(index=1, image_id="b"),
            Card(index=2, image_id="c"),
        ]
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        # Input is now locked
        engine.flip(cards[2])
        assert cards[2].state == CardState.FACE_DOWN

    def test_flip_ignored_for_face_up_card(self):
        cards = _make_mismatch()
        engine = MatchEngine()
        engine.flip(cards[0])
        # Flip the same card again — should be ignored
        result = engine.flip(cards[0])
        assert result is None


class TestBoardClear:
    def test_board_clear_when_all_matched(self):
        cards = _make_pair()
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        event = engine.update(_FLIP_DURATION + 0.01, cards)
        assert event == GameEvent.BOARD_CLEAR

    def test_no_board_clear_when_cards_remain(self):
        cards = _make_pair("pizza_01") + _make_mismatch()
        # Fix indices
        for i, c in enumerate(cards):
            c.index = i
        # cards[0] and cards[1] are a pair, cards[2] and cards[3] are not
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        event = engine.update(_FLIP_DURATION + 0.01, cards)
        # Should be MATCH, not BOARD_CLEAR (other cards still unmatched)
        assert event == GameEvent.MATCH


class TestMismatchDelay:
    def test_delay_is_between_1_and_2_seconds(self):
        """AC-1.3: mismatch display time is 1–2 seconds."""
        assert 1.0 <= _MISMATCH_DELAY <= 2.0

    def test_no_event_during_delay(self):
        cards = _make_mismatch()
        engine = MatchEngine()
        engine.flip(cards[0])
        engine.flip(cards[1])
        engine.update(_FLIP_DURATION + 0.01, cards)
        # Halfway through delay
        event = engine.update(_MISMATCH_DELAY / 2, cards)
        assert event is None
