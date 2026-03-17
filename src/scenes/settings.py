# Implements: REQ-6 AC-6.1, AC-6.4, AC-6.5, AC-6.6 — Settings scene
# See: ARC §src/scenes/settings.py

from __future__ import annotations

import pygame

from src.scenes.base import Scene
from src.theme import THEMES, Theme, ThemeRegistry
from src.ui import Button, FocusGroup, Label


class SettingsScene(Scene):
    """Display and mutate settings (sound, music, animation mode, theme).

    Changes are persisted immediately via ``Settings.save()``.
    """

    def __init__(
        self,
        theme_registry: ThemeRegistry,
        *,
        settings: object | None = None,
        audio_manager: object | None = None,
        scene_manager: object | None = None,
        return_factory: object | None = None,
    ) -> None:
        self._registry = theme_registry
        self._settings = settings
        self._audio_manager = audio_manager
        self._scene_manager = scene_manager
        self._return_factory = return_factory
        self._label = Label()
        self._buttons: list[Button] = []
        self._focus = FocusGroup()
        self._last_surface_size: tuple[int, int] = (0, 0)
        self._build_buttons(pygame.Rect(0, 0, 800, 600))

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_buttons(self, bounds: pygame.Rect) -> None:
        cx = bounds.centerx
        btn_w = max(260, bounds.width // 3)
        btn_h = max(44, bounds.height // 12)
        gap = max(10, btn_h // 4)

        start_y = bounds.centery - (btn_h * 3)
        self._buttons = []

        labels = self._button_labels()
        for i, lbl in enumerate(labels):
            self._buttons.append(
                Button(
                    pygame.Rect(
                        cx - btn_w // 2,
                        start_y + i * (btn_h + gap),
                        btn_w,
                        btn_h,
                    ),
                    lbl,
                )
            )

        self._focus = FocusGroup()
        for btn in self._buttons:
            self._focus.add(btn)

    def _button_labels(self) -> list[str]:
        """Generate button labels reflecting current settings state."""
        if self._settings is None:
            return ["Sound: On", "Music: On", "Animation: Full", "Theme: green", "Back"]

        s = self._settings
        return [
            f"Sound: {'On' if s.sound_enabled else 'Off'}",
            f"Music: {'On' if s.music_enabled else 'Off'}",
            f"Animation: {s.animation_mode.capitalize()}",
            f"Theme: {s.theme}",
            "Back",
        ]

    def _refresh_layout_if_needed(self, surface: pygame.Surface) -> None:
        size = surface.get_size()
        if size != self._last_surface_size:
            self._build_buttons(surface.get_rect())
            self._last_surface_size = size

    # ------------------------------------------------------------------
    # Scene interface
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        activated: Button | None = self._focus.handle_event(event)

        if (
            activated is None
            and event.type == pygame.KEYDOWN
            and event.key == pygame.K_RETURN
        ):
            activated = next((b for b in self._buttons if b.focused), None)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for btn in self._buttons:
                if btn.contains(event.pos):
                    activated = btn
                    break

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_back()
            return

        if activated is not None:
            self._activate(activated.label)

    def _activate(self, label: str) -> None:
        if self._settings is None:
            if label == "Back":
                self._go_back()
            return

        s = self._settings

        if label.startswith("Sound:"):
            s.sound_enabled = not s.sound_enabled
            if self._audio_manager is not None:
                self._audio_manager.set_muted(not s.sound_enabled)
            s.save()
        elif label.startswith("Music:"):
            s.music_enabled = not s.music_enabled
            s.save()
        elif label.startswith("Animation:"):
            s.animation_mode = "reduced" if s.animation_mode == "full" else "full"
            s.save()
        elif label.startswith("Theme:"):
            names = list(THEMES.keys())
            current_idx = names.index(s.theme) if s.theme in names else 0
            s.theme = names[(current_idx + 1) % len(names)]
            self._registry.set_theme(s.theme)
            s.save()
        elif label == "Back":
            self._go_back()
            return

        # Rebuild buttons to update labels
        self._build_buttons(
            pygame.Rect(0, 0, *self._last_surface_size)
            if self._last_surface_size != (0, 0)
            else pygame.Rect(0, 0, 800, 600)
        )

    def _go_back(self) -> None:
        if self._scene_manager is not None and self._return_factory is not None:
            self._scene_manager.switch(self._return_factory())

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self._refresh_layout_if_needed(surface)
        theme: Theme = self._registry.active
        surface.fill(theme.background)

        title_rect = pygame.Rect(
            0, surface.get_height() // 10, surface.get_width(), surface.get_height() // 8
        )
        self._label.draw(surface, "Settings", title_rect, theme, style="title")

        for btn in self._buttons:
            btn.draw(surface, theme)
