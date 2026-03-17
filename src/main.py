# Implements: REQ-7 AC-7.1 AC-7.2 AC-7.3 AC-7.4 — application entry point
# Implements: REQ-1 — wire scene manager and asset loader for game launch
# Implements: REQ-5 — wire SaveManager for save/resume
# Implements: REQ-6 — wire Settings and AudioManager
# See: ARC §src/main.py

import sys

import pygame

from src.assets.loader import AssetLoader
from src.audio import AudioManager
from src.save import SaveManager
from src.scene_manager import SceneManager
from src.scenes.menu import MenuScene
from src.settings import Settings
from src.theme import ThemeRegistry

_INITIAL_WIDTH = 800
_INITIAL_HEIGHT = 600
_TARGET_FPS = 60


def main() -> None:
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode(
        (_INITIAL_WIDTH, _INITIAL_HEIGHT), pygame.RESIZABLE
    )
    pygame.display.set_caption("Delicious Memory")

    theme_registry = ThemeRegistry()
    settings = Settings()
    theme_registry.set_theme(settings.theme)
    audio_manager = AudioManager()
    audio_manager.set_muted(not settings.sound_enabled)
    asset_loader = AssetLoader()
    save_manager = SaveManager()
    menu = MenuScene(theme_registry)
    scene_manager = SceneManager(menu)

    # Wire runtime dependencies so menu can launch the game scene
    menu._scene_manager = scene_manager
    menu._asset_loader = asset_loader
    menu._save_manager = save_manager
    menu._settings = settings
    menu._audio_manager = audio_manager

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(_TARGET_FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
            scene_manager.handle_event(event)

        if not running:
            break

        scene_manager.update(dt)
        scene_manager.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
