# Implements: REQ-1 AC-1.1, AC-1.3, AC-1.4, REQ-2 AC-2.1 — Top-level event loop with screen transitions
# See: ARC §2 (game_loop), ADR-7 (Game State Machine)
from __future__ import annotations

import random

import pygame

from .assets import AssetLoader
from .board import Board
from .card_animator import CardAnimator
from .difficulty import get_difficulty
from .display import Display
from .screens import Screen, ScreenAction
from .screens.game_screen import GameScreen
from .screens.main_menu import MainMenuScreen
from .settings import Settings
from .theme import Theme


class GameLoop:
    """Drives the main event loop, frame timing, and screen transitions."""

    TARGET_FPS = 60

    def __init__(
        self,
        display: Display,
        initial_screen: Screen,
        settings: Settings,
        theme: Theme,
        asset_loader: AssetLoader,
    ) -> None:
        self._display = display
        self._screen: Screen = initial_screen
        self._settings = settings
        self._theme = theme
        self._asset_loader = asset_loader
        self._running = False
        self._clock = pygame.time.Clock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def screen(self) -> Screen:
        return self._screen

    @screen.setter
    def screen(self, value: Screen) -> None:
        self._screen = value

    def request_quit(self) -> None:
        """Signal the loop to terminate."""
        self._running = False

    def run(self) -> None:
        """Blocking loop — returns when ``request_quit`` is called or window is closed."""
        self._running = True
        while self._running:
            dt_ms = self._clock.tick(self.TARGET_FPS)
            self._process_events()
            if not self._running:
                break
            self._screen.update(dt_ms)
            surface = self._display.get_surface()
            self._screen.draw(surface)
            pygame.display.flip()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.request_quit()
                return

            if event.type == pygame.VIDEORESIZE:
                self._display.handle_resize(event.w, event.h)
                continue

            # pygame.ACTIVEEVENT — focus loss/gain: no special handling needed
            # beyond continuing the loop normally (no rendering corruption).
            if event.type == pygame.ACTIVEEVENT:
                continue

            action = self._screen.handle_event(event)
            if action is not None:
                self._handle_action(action)

    def _handle_action(self, action: ScreenAction) -> None:
        if action.action == "quit":
            self.request_quit()
        elif action.action == "start_game":
            difficulty = action.payload.get("difficulty", self._settings.difficulty)
            self._settings.difficulty = difficulty
            self._screen = self._create_game_screen(difficulty)
        elif action.action == "main_menu":
            self._screen = self._create_main_menu()

    def _create_game_screen(self, difficulty: str | None = None) -> GameScreen:
        """Build a new game screen for the given difficulty."""
        diff = get_difficulty(difficulty or self._settings.difficulty)
        num_pairs = (diff.rows * diff.cols) // 2
        card_images = self._asset_loader.load_card_images(
            self._settings.category, num_pairs
        )
        card_back = self._asset_loader.load_card_back()

        # Build shuffled image_id list (each id appears twice)
        image_ids = [img.image_id for img in card_images] * 2
        random.shuffle(image_ids)

        board = Board(diff.rows, diff.cols, image_ids)
        animator = CardAnimator(
            reduced_animation=self._settings.reduced_animation,
        )
        card_surfaces = {img.image_id: img.surface for img in card_images}

        return GameScreen(
            board=board,
            animator=animator,
            display=self._display,
            theme=self._theme,
            card_surfaces=card_surfaces,
            card_back=card_back,
        )

    def _create_main_menu(self) -> MainMenuScreen:
        """Build a fresh main menu screen."""
        return MainMenuScreen(
            display=self._display,
            save_exists=False,
            theme=self._theme,
        )
