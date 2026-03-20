# Implements: REQ-1 AC-1.2, AC-1.3 — Resizable pygame window with coordinate scaling
# See: ARC SS 3 (display)
from __future__ import annotations

import pygame

# Design-space resolution used for proportional layout calculations.
DEFAULT_SIZE: tuple[int, int] = (1024, 768)


class Display:
    """Manages the pygame window surface and provides proportional coordinate scaling."""

    def __init__(
        self,
        title: str = "Delicious Memory",
        default_size: tuple[int, int] = DEFAULT_SIZE,
    ) -> None:
        self._design_width, self._design_height = default_size
        self._width = self._design_width
        self._height = self._design_height
        self._surface: pygame.Surface = pygame.display.set_mode(
            (self._width, self._height), pygame.RESIZABLE
        )
        pygame.display.set_caption(title)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_surface(self) -> pygame.Surface:
        """Return the current window surface."""
        return self._surface

    def handle_resize(self, new_width: int, new_height: int) -> None:
        """Update the window surface after a ``VIDEORESIZE`` event."""
        self._width = max(new_width, 320)
        self._height = max(new_height, 240)
        self._surface = pygame.display.set_mode(
            (self._width, self._height), pygame.RESIZABLE
        )

    def scale_rect(self, base_rect: pygame.Rect) -> pygame.Rect:
        """Map a rect from design-space to the current window size."""
        sx = self._width / self._design_width
        sy = self._height / self._design_height
        return pygame.Rect(
            int(base_rect.x * sx),
            int(base_rect.y * sy),
            int(base_rect.width * sx),
            int(base_rect.height * sy),
        )

    def logical_size(self) -> tuple[int, int]:
        """Return the current window dimensions ``(width, height)``."""
        return (self._width, self._height)

    # Convenience read-only properties
    @property
    def design_width(self) -> int:
        return self._design_width

    @property
    def design_height(self) -> int:
        return self._design_height
