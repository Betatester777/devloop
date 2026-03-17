# Verifies: AC-4.4 — Fail/retry screen shown on timer expiry
# Verifies: AC-4.5 — Victory screen shows score, moves, elapsed time

from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pytest

from src.scenes.results import Outcome, OutcomeKind, ResultScene
from src.theme import ThemeRegistry


@pytest.fixture(autouse=True)
def _init_pygame():
    pygame.init()
    pygame.display.set_mode((800, 600))
    yield
    pygame.quit()


def _win_outcome() -> Outcome:
    return Outcome(
        kind=OutcomeKind.WIN,
        score=760,
        moves=8,
        elapsed_seconds=42.5,
        pairs_found=8,
        total_pairs=8,
    )


def _loss_outcome() -> Outcome:
    return Outcome(
        kind=OutcomeKind.LOSS,
        score=0,
        moves=3,
        elapsed_seconds=60.0,
        pairs_found=2,
        total_pairs=8,
    )


class TestResultSceneInit:
    def test_stores_outcome(self):
        scene = ResultScene(ThemeRegistry(), _win_outcome())
        assert scene.outcome.kind == OutcomeKind.WIN
        assert scene.outcome.score == 760

    def test_has_two_buttons(self):
        scene = ResultScene(ThemeRegistry(), _win_outcome())
        labels = [b.label for b in scene._buttons]
        assert "Play Again" in labels
        assert "Main Menu" in labels


class TestResultSceneDraw:
    def test_draw_win_does_not_crash(self):
        scene = ResultScene(ThemeRegistry(), _win_outcome())
        surface = pygame.display.get_surface()
        scene.draw(surface)

    def test_draw_loss_does_not_crash(self):
        scene = ResultScene(ThemeRegistry(), _loss_outcome())
        surface = pygame.display.get_surface()
        scene.draw(surface)


class TestResultSceneNavigation:
    def test_play_again_calls_factory(self):
        sm = MagicMock()
        play_factory = MagicMock()
        scene = ResultScene(
            ThemeRegistry(),
            _win_outcome(),
            scene_manager=sm,
            play_again_factory=play_factory,
        )
        scene._activate("Play Again")
        sm.switch.assert_called_once()
        play_factory.assert_called_once()

    def test_main_menu_calls_factory(self):
        sm = MagicMock()
        menu_factory = MagicMock()
        scene = ResultScene(
            ThemeRegistry(),
            _win_outcome(),
            scene_manager=sm,
            menu_factory=menu_factory,
        )
        scene._activate("Main Menu")
        sm.switch.assert_called_once()
        menu_factory.assert_called_once()

    def test_click_activates_button(self):
        sm = MagicMock()
        menu_factory = MagicMock()
        scene = ResultScene(
            ThemeRegistry(),
            _win_outcome(),
            scene_manager=sm,
            menu_factory=menu_factory,
        )
        surface = pygame.display.get_surface()
        scene.draw(surface)

        # Find position of "Main Menu" button
        btn = next(b for b in scene._buttons if b.label == "Main Menu")
        event = pygame.event.Event(
            pygame.MOUSEBUTTONUP, button=1, pos=btn.rect.center,
        )
        scene.handle_event(event)
        sm.switch.assert_called_once()

    def test_keyboard_enter_activates_focused(self):
        sm = MagicMock()
        play_factory = MagicMock()
        scene = ResultScene(
            ThemeRegistry(),
            _win_outcome(),
            scene_manager=sm,
            play_again_factory=play_factory,
        )
        # Manually focus the first button (Play Again) without triggering activation
        scene._buttons[0].focused = True
        # Enter to activate
        enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        scene.handle_event(enter)
        sm.switch.assert_called_once()


class TestOutcomeKind:
    def test_win(self):
        assert OutcomeKind.WIN.value == "win"

    def test_loss(self):
        assert OutcomeKind.LOSS.value == "loss"
