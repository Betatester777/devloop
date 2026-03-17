# Verifies: AC-1.2 — Card flip animation (400 ms), state machine transitions
# Verifies: AC-1.4 — Card state guards prevent invalid transitions

from __future__ import annotations

from src.game.card import Card, CardState, _FLIP_DURATION


class TestCardInit:
    def test_initial_state(self):
        card = Card(index=0, image_id="pizza_01")
        assert card.state == CardState.FACE_DOWN
        assert card.flip_progress == 0.0
        assert card.index == 0
        assert card.image_id == "pizza_01"

    def test_not_animating_initially(self):
        card = Card(index=0, image_id="pizza_01")
        assert card.is_animating() is False


class TestFlipUp:
    def test_flip_up_starts_animation(self):
        card = Card(index=0, image_id="pizza_01")
        card.flip_up()
        assert card.state == CardState.FLIPPING_UP
        assert card.is_animating() is True

    def test_flip_up_completes(self):
        card = Card(index=0, image_id="pizza_01")
        card.flip_up()
        card.update(_FLIP_DURATION + 0.01)
        assert card.state == CardState.FACE_UP
        assert card.flip_progress == 1.0
        assert card.is_animating() is False

    def test_flip_up_partial(self):
        card = Card(index=0, image_id="pizza_01")
        card.flip_up()
        card.update(_FLIP_DURATION / 2)
        assert card.state == CardState.FLIPPING_UP
        assert 0.4 < card.flip_progress < 0.6

    def test_flip_up_ignored_when_face_up(self):
        card = Card(index=0, image_id="pizza_01")
        card.flip_up()
        card.update(_FLIP_DURATION + 0.01)
        card.flip_up()  # Should be ignored
        assert card.state == CardState.FACE_UP

    def test_flip_up_ignored_when_matched(self):
        card = Card(index=0, image_id="pizza_01")
        card.mark_matched()
        card.flip_up()  # Should be ignored
        assert card.state == CardState.MATCHED


class TestFlipDown:
    def test_flip_down_starts_animation(self):
        card = Card(index=0, image_id="pizza_01")
        card.flip_up()
        card.update(_FLIP_DURATION + 0.01)
        card.flip_down()
        assert card.state == CardState.FLIPPING_DOWN
        assert card.is_animating() is True

    def test_flip_down_completes(self):
        card = Card(index=0, image_id="pizza_01")
        card.flip_up()
        card.update(_FLIP_DURATION + 0.01)
        card.flip_down()
        card.update(_FLIP_DURATION + 0.01)
        assert card.state == CardState.FACE_DOWN
        assert card.flip_progress == 0.0

    def test_flip_down_ignored_when_face_down(self):
        card = Card(index=0, image_id="pizza_01")
        card.flip_down()
        assert card.state == CardState.FACE_DOWN

    def test_flip_down_ignored_when_matched(self):
        card = Card(index=0, image_id="pizza_01")
        card.mark_matched()
        card.flip_down()
        assert card.state == CardState.MATCHED


class TestMarkMatched:
    def test_mark_matched(self):
        card = Card(index=0, image_id="pizza_01")
        card.mark_matched()
        assert card.state == CardState.MATCHED
        assert card.flip_progress == 1.0
        assert card.is_animating() is False

    def test_matched_is_permanent(self):
        card = Card(index=0, image_id="pizza_01")
        card.mark_matched()
        card.flip_up()
        card.flip_down()
        assert card.state == CardState.MATCHED


class TestUpdate:
    def test_update_noop_when_face_down(self):
        card = Card(index=0, image_id="pizza_01")
        card.update(1.0)
        assert card.state == CardState.FACE_DOWN
        assert card.flip_progress == 0.0

    def test_update_noop_when_matched(self):
        card = Card(index=0, image_id="pizza_01")
        card.mark_matched()
        card.update(1.0)
        assert card.state == CardState.MATCHED
        assert card.flip_progress == 1.0

    def test_flip_duration_is_400ms(self):
        assert _FLIP_DURATION == 0.4


class TestSerialization:
    def test_to_dict(self):
        card = Card(index=3, image_id="pasta_02")
        d = card.to_dict()
        assert d["index"] == 3
        assert d["image_id"] == "pasta_02"
        assert d["state"] == "face_down"
        assert d["flip_progress"] == 0.0

    def test_from_dict_face_down(self):
        d = {"index": 5, "image_id": "cake_01", "state": "face_down", "flip_progress": 0.0}
        card = Card.from_dict(d)
        assert card.index == 5
        assert card.image_id == "cake_01"
        assert card.state == CardState.FACE_DOWN

    def test_from_dict_matched(self):
        d = {"index": 2, "image_id": "pie_03", "state": "matched", "flip_progress": 1.0}
        card = Card.from_dict(d)
        assert card.state == CardState.MATCHED
        assert card.flip_progress == 1.0

    def test_from_dict_mid_animation_resets(self):
        """Mid-animation states reset to FACE_DOWN on load (no mid-animation resume)."""
        d = {"index": 1, "image_id": "soup_01", "state": "flipping_up", "flip_progress": 0.5}
        card = Card.from_dict(d)
        assert card.state == CardState.FACE_DOWN
        assert card.flip_progress == 0.0

    def test_round_trip(self):
        card = Card(index=7, image_id="donut_01")
        card.mark_matched()
        restored = Card.from_dict(card.to_dict())
        assert restored.index == 7
        assert restored.image_id == "donut_01"
        assert restored.state == CardState.MATCHED
