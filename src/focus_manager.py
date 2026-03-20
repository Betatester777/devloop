# Implements: REQ-1 AC-1.1, AC-1.3 — Keyboard focus navigation with visible indicator
# See: ARC SS 15 (focus_manager)
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import pygame

Color = tuple[int, int, int]


class FocusAction(Enum):
    """Actions produced by keyboard navigation."""

    ACTIVATE = auto()
    CANCEL = auto()
    NEXT = auto()
    PREV = auto()
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


@dataclass
class FocusElement:
    """A single focusable UI element."""

    name: str
    rect: pygame.Rect
    selectable: bool = True


class FocusManager:
    """Tracks keyboard focus across a list of :class:`FocusElement` items."""

    INDICATOR_WIDTH = 3

    def __init__(self, elements: list[FocusElement]) -> None:
        self._elements = elements
        self._index: int = 0
        # Jump to first selectable element
        self._advance_to_selectable(forward=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_key(self, key: int) -> FocusAction | None:
        """Map a key press to a :class:`FocusAction` and update internal focus."""
        action = self._key_to_action(key)
        if action is None:
            return None

        if action in (FocusAction.NEXT, FocusAction.DOWN):
            self._move(forward=True)
        elif action in (FocusAction.PREV, FocusAction.UP):
            self._move(forward=False)
        # LEFT/RIGHT are returned but do not move in a vertical list
        return action

    def focused_index(self) -> int:
        return self._index

    def focused_element(self) -> FocusElement:
        return self._elements[self._index]

    def set_focus(self, index: int) -> None:
        if 0 <= index < len(self._elements):
            self._index = index

    def draw_indicator(
        self, surface: pygame.Surface, rect: pygame.Rect, color: Color
    ) -> None:
        """Draw a visible outline around *rect* on *surface*."""
        pygame.draw.rect(surface, color, rect, self.INDICATOR_WIDTH)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _key_to_action(key: int) -> FocusAction | None:
        mapping: dict[int, FocusAction] = {
            pygame.K_TAB: FocusAction.NEXT,
            pygame.K_DOWN: FocusAction.DOWN,
            pygame.K_UP: FocusAction.UP,
            pygame.K_LEFT: FocusAction.LEFT,
            pygame.K_RIGHT: FocusAction.RIGHT,
            pygame.K_RETURN: FocusAction.ACTIVATE,
            pygame.K_KP_ENTER: FocusAction.ACTIVATE,
            pygame.K_ESCAPE: FocusAction.CANCEL,
        }
        return mapping.get(key)

    def _selectable_indices(self) -> list[int]:
        return [i for i, e in enumerate(self._elements) if e.selectable]

    def _move(self, *, forward: bool) -> None:
        selectable = self._selectable_indices()
        if not selectable:
            return
        try:
            pos = selectable.index(self._index)
        except ValueError:
            pos = 0
        if forward:
            pos = (pos + 1) % len(selectable)
        else:
            pos = (pos - 1) % len(selectable)
        self._index = selectable[pos]

    def _advance_to_selectable(self, *, forward: bool) -> None:
        selectable = self._selectable_indices()
        if not selectable:
            return
        if self._index not in selectable:
            self._index = selectable[0]
