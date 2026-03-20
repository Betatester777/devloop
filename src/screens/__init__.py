# Implements: REQ-1 AC-1.1 — Screen protocol, ScreenAction, and ScreenName enum
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

import pygame


class ScreenName(Enum):
    """Identifies each screen the game loop can transition to."""

    MAIN_MENU = "main_menu"
    GAME = "game"
    SETTINGS = "settings"
    VICTORY = "victory"
    FAIL_RETRY = "fail_retry"
    PAUSED = "paused"


@dataclass
class ScreenAction:
    """Returned by Screen.handle_event to request a state transition or command."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


class Screen(Protocol):
    """Protocol that every game screen must implement."""

    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None:
        """Process a single pygame event. Return a ScreenAction to signal the loop."""
        ...

    def update(self, dt_ms: float) -> None:
        """Advance screen state by *dt_ms* milliseconds."""
        ...

    def draw(self, surface: pygame.Surface) -> None:
        """Render the screen onto *surface*."""
        ...
