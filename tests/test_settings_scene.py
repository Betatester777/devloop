# Verifies: AC-6.1 — SettingsScene lists all configurable options
# Verifies: AC-6.4 — Theme change renders immediately
# Verifies: AC-6.5 — Settings toggled and persisted
# Verifies: AC-6.6 — Animation mode toggle

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pygame
import pytest

from src.scenes.settings import SettingsScene
from src.settings import Settings
from src.theme import ThemeRegistry


@pytest.fixture(autouse=True)
def _pygame_init():
    pygame.init()
    yield
    pygame.quit()


def _make_surface(w: int = 800, h: int = 600) -> pygame.Surface:
    return pygame.Surface((w, h))


def _make_scene(
    tmp_path: Path | None = None,
) -> tuple[SettingsScene, Settings, ThemeRegistry]:
    registry = ThemeRegistry()
    settings = Settings(settings_path=tmp_path / "s.json") if tmp_path else Settings(settings_path=Path("/tmp/test_settings_scene.json"))
    scene = SettingsScene(
        registry,
        settings=settings,
        audio_manager=MagicMock(),
        scene_manager=MagicMock(),
        return_factory=MagicMock(),
    )
    return scene, settings, registry


class TestSettingsSceneOptions:
    """AC-6.1: all configurable options visibly listed."""

    def test_four_setting_buttons_plus_back(self, tmp_path: Path):
        scene, _, _ = _make_scene(tmp_path)
        surface = _make_surface()
        scene.draw(surface)
        labels = {btn.label for btn in scene._buttons}
        assert any("Sound" in lbl for lbl in labels)
        assert any("Music" in lbl for lbl in labels)
        assert any("Animation" in lbl for lbl in labels)
        assert any("Theme" in lbl for lbl in labels)
        assert "Back" in labels

    def test_five_buttons_total(self, tmp_path: Path):
        scene, _, _ = _make_scene(tmp_path)
        assert len(scene._buttons) == 5


class TestSettingsSceneToggle:
    """AC-6.5: settings toggled and persisted."""

    def test_toggle_sound(self, tmp_path: Path):
        scene, settings, _ = _make_scene(tmp_path)
        surface = _make_surface()
        scene.draw(surface)
        assert settings.sound_enabled is True
        sound_btn = next(b for b in scene._buttons if "Sound" in b.label)
        click = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=sound_btn.rect.center)
        scene.handle_event(click)
        assert settings.sound_enabled is False

    def test_toggle_music(self, tmp_path: Path):
        scene, settings, _ = _make_scene(tmp_path)
        surface = _make_surface()
        scene.draw(surface)
        music_btn = next(b for b in scene._buttons if "Music" in b.label)
        click = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=music_btn.rect.center)
        scene.handle_event(click)
        assert settings.music_enabled is False

    def test_toggle_animation_mode(self, tmp_path: Path):
        """AC-6.6: reduced animation mode toggle."""
        scene, settings, _ = _make_scene(tmp_path)
        surface = _make_surface()
        scene.draw(surface)
        anim_btn = next(b for b in scene._buttons if "Animation" in b.label)
        click = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=anim_btn.rect.center)
        scene.handle_event(click)
        assert settings.animation_mode == "reduced"
        # Toggle back
        anim_btn = next(b for b in scene._buttons if "Animation" in b.label)
        click = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=anim_btn.rect.center)
        scene.handle_event(click)
        assert settings.animation_mode == "full"


class TestSettingsSceneTheme:
    """AC-6.4: theme change renders immediately."""

    def test_theme_switch(self, tmp_path: Path):
        scene, settings, registry = _make_scene(tmp_path)
        surface = _make_surface()
        scene.draw(surface)
        assert registry.active.name == "green"
        theme_btn = next(b for b in scene._buttons if "Theme" in b.label)
        click = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=theme_btn.rect.center)
        scene.handle_event(click)
        assert registry.active.name == "neutral"
        assert settings.theme == "neutral"


class TestSettingsSceneNavigation:
    def test_back_button_returns(self, tmp_path: Path):
        scene, _, _ = _make_scene(tmp_path)
        surface = _make_surface()
        scene.draw(surface)
        back_btn = next(b for b in scene._buttons if b.label == "Back")
        click = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=back_btn.rect.center)
        scene.handle_event(click)
        scene._scene_manager.switch.assert_called_once()

    def test_escape_returns(self, tmp_path: Path):
        scene, _, _ = _make_scene(tmp_path)
        esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        scene.handle_event(esc)
        scene._scene_manager.switch.assert_called_once()

    def test_draw_does_not_crash(self, tmp_path: Path):
        scene, _, _ = _make_scene(tmp_path)
        surface = _make_surface()
        scene.draw(surface)  # No exception
