# Verifies: AC-1.1, AC-1.3 — Focus navigation cycling, activate/cancel actions
from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from src.focus_manager import FocusAction, FocusElement, FocusManager  # noqa: E402


@pytest.fixture(autouse=True)
def _init_pygame():
    pygame.init()
    yield
    pygame.quit()


def _make_elements(count: int = 4, all_selectable: bool = True) -> list[FocusElement]:
    return [
        FocusElement(
            name=f"btn_{i}",
            rect=pygame.Rect(0, i * 60, 200, 50),
            selectable=all_selectable,
        )
        for i in range(count)
    ]


class TestNavigation:
    def test_initial_focus_is_first(self) -> None:
        fm = FocusManager(_make_elements())
        assert fm.focused_index() == 0

    def test_tab_cycles_forward(self) -> None:
        fm = FocusManager(_make_elements(3))
        fm.handle_key(pygame.K_TAB)
        assert fm.focused_index() == 1
        fm.handle_key(pygame.K_TAB)
        assert fm.focused_index() == 2
        fm.handle_key(pygame.K_TAB)
        assert fm.focused_index() == 0  # wraps

    def test_down_arrow_moves_forward(self) -> None:
        fm = FocusManager(_make_elements(3))
        fm.handle_key(pygame.K_DOWN)
        assert fm.focused_index() == 1

    def test_up_arrow_moves_backward(self) -> None:
        fm = FocusManager(_make_elements(3))
        fm.handle_key(pygame.K_UP)
        assert fm.focused_index() == 2  # wraps to last

    def test_skips_non_selectable(self) -> None:
        elements = _make_elements(3)
        elements[1].selectable = False
        fm = FocusManager(elements)
        fm.handle_key(pygame.K_TAB)
        assert fm.focused_index() == 2  # skipped index 1

    def test_initial_focus_skips_non_selectable_first(self) -> None:
        elements = _make_elements(3)
        elements[0].selectable = False
        fm = FocusManager(elements)
        assert fm.focused_index() == 1


class TestActions:
    def test_enter_returns_activate(self) -> None:
        fm = FocusManager(_make_elements())
        action = fm.handle_key(pygame.K_RETURN)
        assert action is FocusAction.ACTIVATE

    def test_escape_returns_cancel(self) -> None:
        fm = FocusManager(_make_elements())
        action = fm.handle_key(pygame.K_ESCAPE)
        assert action is FocusAction.CANCEL

    def test_unknown_key_returns_none(self) -> None:
        fm = FocusManager(_make_elements())
        action = fm.handle_key(pygame.K_a)
        assert action is None


class TestSetFocus:
    def test_set_focus_to_valid_index(self) -> None:
        fm = FocusManager(_make_elements())
        fm.set_focus(2)
        assert fm.focused_index() == 2

    def test_set_focus_out_of_range_ignored(self) -> None:
        fm = FocusManager(_make_elements())
        fm.set_focus(99)
        assert fm.focused_index() == 0  # unchanged


class TestDrawIndicator:
    def test_draw_indicator_does_not_crash(self) -> None:
        fm = FocusManager(_make_elements())
        surface = pygame.Surface((800, 600))
        fm.draw_indicator(surface, pygame.Rect(10, 10, 100, 50), (0, 255, 0))
        # No assertion needed — just confirming no exception
