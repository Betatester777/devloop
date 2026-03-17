# Implements: REQ-7 AC-7.2 AC-7.3 — Button, Label, FocusGroup widgets
# See: ARC §src/ui.py

from __future__ import annotations

import pygame

from src.theme import Theme


class Button:
    """A clickable button widget with optional keyboard focus."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        enabled: bool = True,
    ) -> None:
        self.rect = rect
        self.label = label
        self.focused = False
        self.enabled = enabled

    def draw(self, surface: pygame.Surface, theme: Theme) -> None:
        colour = theme.primary if self.enabled else theme.text_muted
        pygame.draw.rect(surface, colour, self.rect, border_radius=6)
        if self.focused:
            pygame.draw.rect(
                surface, theme.focus_ring, self.rect, width=3, border_radius=6
            )
        font = pygame.font.SysFont(None, 28)
        text_surf = font.render(self.label, True, theme.on_primary)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class Label:
    """Stateless text drawing helper with style variants."""

    _FONT_SIZES: dict[str, int] = {
        "title": 56,
        "heading": 40,
        "body": 28,
        "caption": 20,
    }

    def draw(
        self,
        surface: pygame.Surface,
        text: str,
        rect: pygame.Rect,
        theme: Theme,
        style: str = "body",
    ) -> None:
        size = self._FONT_SIZES.get(style, 28)
        font = pygame.font.SysFont(None, size)
        colour = theme.text_muted if style == "caption" else theme.text
        text_surf = font.render(text, True, colour)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)


class FocusGroup:
    """Tracks keyboard focus across a list of Buttons (Tab / Shift-Tab)."""

    def __init__(self) -> None:
        self._buttons: list[Button] = []

    def add(self, button: Button) -> None:
        self._buttons.append(button)

    def handle_event(self, event: pygame.event.Event) -> Button | None:
        """Advance focus on Tab / Shift-Tab. Returns the newly focused Button."""
        if event.type != pygame.KEYDOWN or event.key != pygame.K_TAB:
            return None

        enabled = [b for b in self._buttons if b.enabled]
        if not enabled:
            return None

        focused_idx = next(
            (i for i, b in enumerate(enabled) if b.focused), -1
        )
        self.clear_focus()
        shift = bool(event.mod & pygame.KMOD_SHIFT)
        if shift:
            next_idx = (focused_idx - 1) % len(enabled)
        else:
            next_idx = (focused_idx + 1) % len(enabled)
        enabled[next_idx].focused = True
        return enabled[next_idx]

    def clear_focus(self) -> None:
        for button in self._buttons:
            button.focused = False
