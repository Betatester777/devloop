# Verifies: AC-2.1 through AC-2.5 — Game board screen with card interaction
from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from src.board import Board, CardState  # noqa: E402
from src.card_animator import CardAnimator  # noqa: E402
from src.display import Display  # noqa: E402
from src.screens.game_screen import GameScreen  # noqa: E402
from src.theme import LIGHT_THEME  # noqa: E402


@pytest.fixture(autouse=True)
def _init_pygame():
    pygame.init()
    yield
    pygame.quit()


def _make_game_screen(
    rows: int = 2,
    cols: int = 2,
    image_ids: list[str] | None = None,
    reduced: bool = True,
) -> GameScreen:
    """Build a GameScreen with a known board layout."""
    if image_ids is None:
        image_ids = ["A", "A", "B", "B"]
    board = Board(rows, cols, image_ids)
    animator = CardAnimator(reduced_animation=reduced)
    display = Display(title="Test", default_size=(1024, 768))
    # Simple colored placeholder surfaces
    unique_ids = set(image_ids)
    card_surfaces = {}
    for uid in unique_ids:
        s = pygame.Surface((100, 140))
        s.fill((100, 100, 100))
        card_surfaces[uid] = s
    card_back = pygame.Surface((100, 140))
    card_back.fill((0, 128, 60))
    return GameScreen(
        board=board,
        animator=animator,
        display=display,
        theme=LIGHT_THEME,
        card_surfaces=card_surfaces,
        card_back=card_back,
    )


class TestKeyboardNavigation:
    def test_cursor_moves_down(self) -> None:
        gs = _make_game_screen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, mod=0, unicode="", scancode=0)
        gs.handle_event(event)
        assert gs._cursor_row == 1

    def test_cursor_wraps_around(self) -> None:
        gs = _make_game_screen()
        # Move down twice on a 2-row board wraps to 0
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, mod=0, unicode="", scancode=0)
        gs.handle_event(event)
        gs.handle_event(event)
        assert gs._cursor_row == 0

    def test_cursor_moves_right(self) -> None:
        gs = _make_game_screen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=0, unicode="", scancode=0)
        gs.handle_event(event)
        assert gs._cursor_col == 1


class TestCardFlip:
    def test_enter_flips_card(self) -> None:
        """AC-2.2: Enter key flips the card at cursor position."""
        gs = _make_game_screen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r", scancode=0)
        gs.handle_event(event)
        assert gs._board.get_card(0, 0).state is CardState.FACE_UP

    def test_space_flips_card(self) -> None:
        gs = _make_game_screen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode=" ", scancode=0)
        gs.handle_event(event)
        assert gs._board.get_card(0, 0).state is CardState.FACE_UP


class TestMatchFlow:
    def test_matching_pair_becomes_matched(self) -> None:
        """AC-2.3: Matching pair stays face-up after animation completes."""
        # Board: A A B B — (0,0) and (0,1) are the same
        gs = _make_game_screen(image_ids=["A", "A", "B", "B"], reduced=True)

        # Flip first card
        enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r", scancode=0)
        gs.handle_event(enter)
        gs.update(0)  # instant flip completes

        # Move right and flip second card
        right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=0, unicode="", scancode=0)
        gs.handle_event(right)
        gs.handle_event(enter)
        gs.update(0)  # instant flip completes, triggers match evaluation

        assert gs._board.get_card(0, 0).state is CardState.MATCHED
        assert gs._board.get_card(0, 1).state is CardState.MATCHED

    def test_mismatched_pair_resets_after_delay(self) -> None:
        """AC-2.4: Mismatched pair flips back after delay."""
        # Board: A B A B — (0,0)=A and (0,1)=B are different
        gs = _make_game_screen(image_ids=["A", "B", "A", "B"], reduced=True)

        enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r", scancode=0)
        gs.handle_event(enter)
        gs.update(0)  # first flip completes

        right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=0, unicode="", scancode=0)
        gs.handle_event(right)
        gs.handle_event(enter)
        gs.update(0)  # second flip completes, triggers mismatch delay

        # Cards should still be face up during delay
        assert gs._board.get_card(0, 0).state is CardState.FACE_UP
        assert gs._board.get_card(0, 1).state is CardState.FACE_UP

        # Advance past mismatch delay (500ms minimum in reduced mode)
        gs.update(500)

        assert gs._board.get_card(0, 0).state is CardState.FACE_DOWN
        assert gs._board.get_card(0, 1).state is CardState.FACE_DOWN


class TestInputGating:
    """AC-2.5: Input blocked during animation."""

    def test_input_blocked_during_flip_animation(self) -> None:
        # Use normal animation (not reduced) so the flip takes time
        gs = _make_game_screen(reduced=False)

        enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r", scancode=0)
        gs.handle_event(enter)
        # Advance partially — animation still running
        gs.update(100)

        # Try to flip another card — should be blocked by animation
        right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=0, unicode="", scancode=0)
        result = gs.handle_event(right)
        assert result is None
        # Cursor should NOT have moved because input is blocked during animation
        assert gs._cursor_col == 0


class TestEscapeToMenu:
    def test_escape_returns_main_menu_action(self) -> None:
        gs = _make_game_screen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode="\x1b", scancode=0)
        action = gs.handle_event(event)
        assert action is not None
        assert action.action == "main_menu"

    def test_escape_during_animation(self) -> None:
        """Escape still works during animation."""
        gs = _make_game_screen(reduced=False)
        enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r", scancode=0)
        gs.handle_event(enter)
        gs.update(100)  # animation in progress

        escape = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode="\x1b", scancode=0)
        action = gs.handle_event(escape)
        assert action is not None
        assert action.action == "main_menu"


class TestDraw:
    def test_draw_does_not_crash(self) -> None:
        gs = _make_game_screen()
        surface = pygame.Surface((1024, 768))
        gs.draw(surface)  # Should not raise
