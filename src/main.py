# Implements: REQ-1 AC-1.1, AC-1.4, REQ-2 AC-2.1 — Application entry point
# See: ARC §1 (main)
from __future__ import annotations

import sys
from pathlib import Path

import pygame

from .assets import AssetLoader
from .display import Display
from .game_loop import GameLoop
from .screens.main_menu import MainMenuScreen
from .settings import Settings, SettingsManager
from .theme import get_theme


def main() -> None:
    """Initialize pygame, build the main menu, and run the game loop."""
    try:
        pygame.init()
    except pygame.error as exc:
        print(f"pygame init failed: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        manager = SettingsManager()
        settings: Settings = manager.load()

        theme = get_theme(settings.theme_name)
        display = Display(title="Delicious Memory")
        asset_loader = AssetLoader(base_path=Path(__file__).resolve().parent / "assets")

        # TODO: check for existing save file once SaveManager is implemented
        save_exists = False

        menu = MainMenuScreen(display=display, save_exists=save_exists, theme=theme)
        loop = GameLoop(
            display=display,
            initial_screen=menu,
            settings=settings,
            theme=theme,
            asset_loader=asset_loader,
        )
        loop.run()
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
