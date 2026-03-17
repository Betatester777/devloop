# Verifies: AC-7.2 AC-7.3 — Button.contains, FocusGroup Tab navigation, disabled skip
# Requirement: REQ-7 (Responsive desktop UI)

import pygame
import pytest

from src.ui import Button, FocusGroup


@pytest.fixture(autouse=True)
def _pygame_init():
    pygame.init()
    yield
    pygame.quit()


def _btn(x: int, y: int, w: int, h: int, label: str = "X", enabled: bool = True) -> Button:
    return Button(pygame.Rect(x, y, w, h), label, enabled=enabled)


class TestButtonContains:
    def test_interior_point_returns_true(self):
        btn = _btn(10, 10, 100, 50)
        assert btn.contains((60, 35))

    def test_exterior_point_returns_false(self):
        btn = _btn(10, 10, 100, 50)
        assert not btn.contains((200, 200))


class TestFocusGroup:
    def _tab(self, shift: bool = False) -> pygame.event.Event:
        mod = pygame.KMOD_SHIFT if shift else pygame.KMOD_NONE
        return pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_TAB, mod=mod, unicode="\t", scancode=0
        )

    def test_tab_advances_focus_to_next(self):
        group = FocusGroup()
        btns = [_btn(0, i * 60, 100, 50, str(i)) for i in range(3)]
        for b in btns:
            group.add(b)
        btns[0].focused = True
        group.handle_event(self._tab())
        assert btns[1].focused

    def test_tab_wraps_from_last_to_first(self):
        group = FocusGroup()
        btns = [_btn(0, i * 60, 100, 50, str(i)) for i in range(3)]
        for b in btns:
            group.add(b)
        btns[2].focused = True
        group.handle_event(self._tab())
        assert btns[0].focused

    def test_disabled_button_is_skipped_on_tab(self):
        group = FocusGroup()
        b0 = _btn(0, 0, 100, 50, "A")
        b1 = _btn(0, 60, 100, 50, "B", enabled=False)
        b2 = _btn(0, 120, 100, 50, "C")
        for b in (b0, b1, b2):
            group.add(b)
        b0.focused = True
        group.handle_event(self._tab())
        assert b2.focused
        assert not b1.focused
