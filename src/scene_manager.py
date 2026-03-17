# Implements: REQ-7 AC-7.1 AC-7.3 AC-7.4 — SceneManager
# See: ARC §src/scene_manager.py

import pygame

from src.scenes.base import Scene


class SceneManager:
    """Owns the active scene reference and forwards lifecycle calls to it."""

    def __init__(self, initial_scene: Scene) -> None:
        self.current: Scene = initial_scene

    def switch(self, scene: Scene) -> None:
        self.current = scene

    def handle_event(self, event: pygame.event.Event) -> None:
        self.current.handle_event(event)

    def update(self, dt: float) -> None:
        self.current.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.current.draw(surface)
