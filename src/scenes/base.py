# Implements: REQ-7 AC-7.1 AC-7.3 — Scene abstract base class
# See: ARC §src/scenes/base.py

from abc import ABC, abstractmethod

import pygame


class Scene(ABC):
    """Abstract base class that all game scenes must implement."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...
