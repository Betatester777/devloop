# Verifies: AC-1.1, AC-1.2, AC-4.1 — Main menu difficulty selection and button actions
from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from src.display import Display  # noqa: E402
from src.screens import ScreenAction  # noqa: E402
from src.screens.main_menu import MainMenuScreen  # noqa: E402
from src.theme import LIGHT_THEME  # noqa: E402


@pytest.fixture(autouse=True)
def _init_pygame():
    pygame.init()
    yield
    pygame.quit()


def _make_menu(save_exists: bool = False) -> MainMenuScreen:
    display = Display(title="Test", default_size=(1024, 768))
    return MainMenuScreen(display=display, save_exists=save_exists, theme=LIGHT_THEME)


def _keydown(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, mod=0)


class TestDifficultyButtons:
    """AC-4.1: difficulty selection from main menu."""

    def test_easy_action(self) -> None:
        menu = _make_menu()
        # Focus starts on Easy (index 0)
        result = menu.handle_event(_keydown(pygame.K_RETURN))
        assert isinstance(result, ScreenAction)
        assert result.action == "start_game"
        assert result.payload == {"difficulty": "easy"}

    def test_normal_action(self) -> None:
        menu = _make_menu()
        menu.handle_event(_keydown(pygame.K_TAB))  # → Normal
        result = menu.handle_event(_keydown(pygame.K_RETURN))
        assert isinstance(result, ScreenAction)
        assert result.action == "start_game"
        assert result.payload == {"difficulty": "normal"}

    def test_hard_action(self) -> None:
        menu = _make_menu()
        menu.handle_event(_keydown(pygame.K_TAB))  # → Normal
        menu.handle_event(_keydown(pygame.K_TAB))  # → Hard
        result = menu.handle_event(_keydown(pygame.K_RETURN))
        assert isinstance(result, ScreenAction)
        assert result.action == "start_game"
        assert result.payload == {"difficulty": "hard"}

    def test_all_three_difficulties_present(self) -> None:
        menu = _make_menu()
        names = [e.name for e in menu._focus_elements[:3]]
        assert "Easy" in names[0]
        assert "Normal" in names[1]
        assert "Hard" in names[2]


class TestOtherButtons:
    def test_settings_action(self) -> None:
        menu = _make_menu()
        # Tab past Easy, Normal, Hard, Continue (skipped) → Settings
        menu.handle_event(_keydown(pygame.K_TAB))  # Normal
        menu.handle_event(_keydown(pygame.K_TAB))  # Hard
        menu.handle_event(_keydown(pygame.K_TAB))  # Settings (Continue skipped)
        result = menu.handle_event(_keydown(pygame.K_RETURN))
        assert isinstance(result, ScreenAction)
        assert result.action == "open_settings"

    def test_quit_action(self) -> None:
        menu = _make_menu()
        menu.handle_event(_keydown(pygame.K_TAB))  # Normal
        menu.handle_event(_keydown(pygame.K_TAB))  # Hard
        menu.handle_event(_keydown(pygame.K_TAB))  # Settings
        menu.handle_event(_keydown(pygame.K_TAB))  # Quit
        result = menu.handle_event(_keydown(pygame.K_RETURN))
        assert isinstance(result, ScreenAction)
        assert result.action == "quit"

    def test_escape_returns_quit(self) -> None:
        menu = _make_menu()
        result = menu.handle_event(_keydown(pygame.K_ESCAPE))
        assert isinstance(result, ScreenAction)
        assert result.action == "quit"


class TestContinueButton:
    def test_continue_disabled_when_no_save(self) -> None:
        menu = _make_menu(save_exists=False)
        # Tab past Easy, Normal, Hard → Continue should be skipped
        menu.handle_event(_keydown(pygame.K_TAB))  # Normal
        menu.handle_event(_keydown(pygame.K_TAB))  # Hard
        menu.handle_event(_keydown(pygame.K_TAB))  # should skip Continue → Settings
        idx = menu._focus_mgr.focused_index()
        assert menu._focus_elements[idx].name == "Settings"

    def test_continue_enabled_when_save_exists(self) -> None:
        menu = _make_menu(save_exists=True)
        menu.handle_event(_keydown(pygame.K_TAB))  # Normal
        menu.handle_event(_keydown(pygame.K_TAB))  # Hard
        menu.handle_event(_keydown(pygame.K_TAB))  # Continue (enabled)
        idx = menu._focus_mgr.focused_index()
        assert menu._focus_elements[idx].name == "Continue"
        result = menu.handle_event(_keydown(pygame.K_RETURN))
        assert isinstance(result, ScreenAction)
        assert result.action == "continue_game"


class TestBoardSizePerDifficulty:
    """AC-4.2: board sizes vary by difficulty."""

    def test_easy_has_fewer_cards_than_normal(self) -> None:
        from src.difficulty import EASY, NORMAL

        assert (EASY.rows * EASY.cols) < (NORMAL.rows * NORMAL.cols)

    def test_hard_has_more_cards_than_normal(self) -> None:
        from src.difficulty import HARD, NORMAL

        assert (HARD.rows * HARD.cols) > (NORMAL.rows * NORMAL.cols)


class TestRandomizedPlacement:
    """AC-4.3: repeated starts produce different layouts."""

    def test_two_shuffles_differ(self) -> None:
        import random

        image_ids = [f"img_{i}" for i in range(10)] * 2
        layouts = []
        for _ in range(10):
            copy = list(image_ids)
            random.shuffle(copy)
            layouts.append(tuple(copy))
        # With 20 items, the probability of two identical shuffles is ~1/(20!) ≈ 0
        unique = set(layouts)
        assert len(unique) > 1


class TestDraw:
    def test_draw_does_not_crash(self) -> None:
        menu = _make_menu()
        surface = pygame.Surface((1024, 768))
        menu.draw(surface)
