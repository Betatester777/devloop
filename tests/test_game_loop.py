# Verifies: AC-1.1, AC-1.3, AC-1.4 — Quit action triggers shutdown, VIDEORESIZE delegated
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from src.assets import AssetLoader  # noqa: E402
from src.display import Display  # noqa: E402
from src.game_loop import GameLoop  # noqa: E402
from src.screens import ScreenAction  # noqa: E402
from src.settings import Settings  # noqa: E402
from src.theme import LIGHT_THEME  # noqa: E402


# ---------------------------------------------------------------------------
# Stub screen for testing
# ---------------------------------------------------------------------------
class _StubScreen:
    """Minimal screen that returns a pre-configured action on the first event."""

    def __init__(self, action: ScreenAction | None = None) -> None:
        self._action = action
        self.events_received: list[pygame.event.Event] = []
        self.update_calls: int = 0
        self.draw_calls: int = 0

    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None:
        self.events_received.append(event)
        action = self._action
        # Only fire once
        self._action = None
        return action

    def update(self, dt_ms: float) -> None:
        self.update_calls += 1

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_calls += 1


@pytest.fixture(autouse=True)
def _init_pygame():
    pygame.init()
    yield
    pygame.quit()


def _make_loop(screen: _StubScreen | None = None) -> GameLoop:
    display = Display(title="Test", default_size=(1024, 768))
    return GameLoop(
        display=display,
        initial_screen=screen or _StubScreen(),
        settings=Settings(),
        theme=LIGHT_THEME,
        asset_loader=AssetLoader(base_path=Path("assets")),
    )


class TestQuitAction:
    def test_request_quit_stops_loop(self) -> None:
        """request_quit() called during event processing terminates the loop."""
        stub = _StubScreen(action=ScreenAction(action="quit"))
        loop = _make_loop(stub)
        # Post a keydown so the screen's handle_event fires and returns "quit"
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, mod=0, unicode="q", scancode=0))
        loop.run()
        # If we reach here the loop exited — pass

    def test_pygame_quit_event_stops_loop(self) -> None:
        """Posting a QUIT event causes the loop to terminate."""
        loop = _make_loop()
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        loop.run()
        # If we reach here the loop exited — pass


class TestVideoResize:
    def test_resize_updates_display(self) -> None:
        display = Display(title="Test", default_size=(1024, 768))
        screen = _StubScreen()
        loop = GameLoop(
            display=display,
            initial_screen=screen,
            settings=Settings(),
            theme=LIGHT_THEME,
            asset_loader=AssetLoader(base_path=Path("assets")),
        )

        # Post resize then quit so the loop processes both
        pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE, w=800, h=600))
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        loop.run()

        assert display.logical_size() == (800, 600)


class TestScreenActionQuit:
    def test_screen_action_quit_terminates(self) -> None:
        """When a screen returns ScreenAction('quit'), the loop stops."""
        stub = _StubScreen(action=ScreenAction(action="quit"))
        loop = _make_loop(stub)

        # We need a non-quit event to reach handle_event in the screen
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, mod=0, unicode="q", scancode=0))
        loop.run()
        # If we reach here the loop exited — pass


class TestActiveEvent:
    def test_active_event_does_not_crash(self) -> None:
        """pygame.ACTIVEEVENT (alt-tab) is handled without errors."""
        stub = _StubScreen()
        loop = _make_loop(stub)

        pygame.event.post(
            pygame.event.Event(pygame.ACTIVEEVENT, gain=0, state=2)
        )
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        loop.run()
        # No crash = pass
