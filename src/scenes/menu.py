# Implements: REQ-7 AC-7.1 AC-7.2 AC-7.3 AC-7.4 — main menu scene
# Implements: REQ-3 AC-3.1 AC-3.3 — difficulty selector on main menu
# Implements: REQ-1 AC-1.1 — launch game scene from menu
# Implements: REQ-5 AC-5.3, AC-5.4 — Continue button with save detection and error handling
# Implements: REQ-6 AC-6.1 — Settings button launches SettingsScene
# See: ARC §src/scenes/menu.py

from __future__ import annotations

import random

import pygame

from src.game.board import Difficulty
from src.scenes.base import Scene
from src.theme import Theme, ThemeRegistry
from src.ui import Button, FocusGroup, Label

_DIFFICULTY_LABELS = {
    "Easy": Difficulty.EASY,
    "Normal": Difficulty.NORMAL,
    "Hard": Difficulty.HARD,
}


class MenuScene(Scene):
    """Main menu with difficulty selector, New Game, Settings, and Quit buttons."""

    def __init__(
        self,
        theme_registry: ThemeRegistry,
        *,
        scene_manager: object | None = None,
        asset_loader: object | None = None,
        save_manager: object | None = None,
        settings: object | None = None,
        audio_manager: object | None = None,
    ) -> None:
        self._registry = theme_registry
        self._scene_manager = scene_manager
        self._asset_loader = asset_loader
        self._save_manager = save_manager
        self._settings = settings
        self._audio_manager = audio_manager
        self._label = Label()
        self._buttons: list[Button] = []
        self._difficulty_buttons: list[Button] = []
        self._focus = FocusGroup()
        self._selected_difficulty: Difficulty = Difficulty.NORMAL
        self._error_message: str = ""
        self._error_timer: float = 0.0
        self._last_surface_size: tuple[int, int] = (0, 0)
        self._build_buttons(pygame.Rect(0, 0, 800, 600))

    @property
    def selected_difficulty(self) -> Difficulty:
        return self._selected_difficulty

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_buttons(self, bounds: pygame.Rect) -> None:
        """Create button objects with proportional layout inside *bounds*."""
        cx = bounds.centerx
        btn_w = max(200, bounds.width // 4)
        btn_h = max(48, bounds.height // 10)
        gap = max(12, btn_h // 3)

        # Difficulty row: three smaller buttons side by side
        diff_btn_w = max(100, btn_w // 2)
        diff_total_w = 3 * diff_btn_w + 2 * gap
        diff_start_x = cx - diff_total_w // 2
        diff_y = bounds.centery - btn_h * 3 - gap * 2

        self._difficulty_buttons = []
        for i, label in enumerate(_DIFFICULTY_LABELS):
            self._difficulty_buttons.append(
                Button(
                    pygame.Rect(
                        diff_start_x + i * (diff_btn_w + gap),
                        diff_y,
                        diff_btn_w,
                        btn_h,
                    ),
                    label,
                )
            )
        # Mark the selected difficulty button
        self._sync_difficulty_focus()

        # Action buttons below difficulty row
        has_save = (
            self._save_manager is not None
            and self._save_manager.has_save()
        )
        action_defs: list[tuple[str, bool]] = [
            ("Continue", has_save),
            ("New Game", True),
            ("Settings", True),
            ("Quit", True),
        ]
        start_y = diff_y + btn_h + gap * 2
        self._buttons = [
            Button(
                pygame.Rect(
                    cx - btn_w // 2,
                    start_y + i * (btn_h + gap),
                    btn_w,
                    btn_h,
                ),
                lbl,
                enabled=enabled,
            )
            for i, (lbl, enabled) in enumerate(action_defs)
        ]

        # Build focus group: difficulty buttons then action buttons
        self._focus = FocusGroup()
        for btn in self._difficulty_buttons:
            self._focus.add(btn)
        for btn in self._buttons:
            self._focus.add(btn)

    def _sync_difficulty_focus(self) -> None:
        """Update difficulty button visuals to reflect the current selection."""
        for btn in self._difficulty_buttons:
            diff = _DIFFICULTY_LABELS.get(btn.label)
            btn.enabled = diff != self._selected_difficulty

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
            activated = next(
                (b for b in self._difficulty_buttons + self._buttons if b.focused),
                None,
            )

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for btn in self._difficulty_buttons + self._buttons:
                if btn.contains(event.pos):
                    activated = btn
                    break

        if activated is not None:
            self._activate(activated.label)

    def _activate(self, label: str) -> None:
        if label in _DIFFICULTY_LABELS:
            self._selected_difficulty = _DIFFICULTY_LABELS[label]
            self._sync_difficulty_focus()
        elif label == "Continue":
            self._continue_game()
        elif label == "New Game":
            self._start_game()
        elif label == "Settings":
            self._open_settings()
        elif label == "Quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _open_settings(self) -> None:
        """Open the settings scene (AC-6.1)."""
        if self._scene_manager is None:
            return
        from src.scenes.settings import SettingsScene

        registry = self._registry
        sm = self._scene_manager
        loader = self._asset_loader
        sav = self._save_manager
        sett = self._settings
        aud = self._audio_manager

        self._scene_manager.switch(
            SettingsScene(
                registry,
                settings=sett,
                audio_manager=aud,
                scene_manager=sm,
                return_factory=lambda: MenuScene(
                    registry,
                    scene_manager=sm,
                    asset_loader=loader,
                    save_manager=sav,
                    settings=sett,
                    audio_manager=aud,
                ),
            )
        )

    def _continue_game(self) -> None:
        """Resume from saved state (AC-5.3, AC-5.4)."""
        if self._scene_manager is None or self._asset_loader is None:
            return
        if self._save_manager is None:
            return

        from src.save import SaveError
        from src.scenes.game import GameScene

        try:
            state = self._save_manager.load()
        except SaveError as exc:
            self._error_message = str(exc)
            self._error_timer = 3.0
            self._save_manager.delete()
            self._build_buttons(pygame.Rect(*self._last_surface_size and (0, 0, *self._last_surface_size) or (0, 0, 800, 600)))
            return

        registry = self._registry
        sm = self._scene_manager
        loader = self._asset_loader
        sav = self._save_manager
        sett = self._settings
        aud = self._audio_manager

        game = GameScene(
            registry,
            state.difficulty,
            state.category,
            loader,
            scene_manager=sm,
            save_manager=sav,
            settings=sett,
            audio_manager=aud,
            menu_factory=lambda: MenuScene(
                registry, scene_manager=sm, asset_loader=loader,
                save_manager=sav, settings=sett, audio_manager=aud,
            ),
            game_state=state,
        )
        sm.switch(game)  # type: ignore[union-attr]

    def _start_game(self) -> None:
        """Launch a new GameScene with the selected difficulty."""
        if self._scene_manager is None or self._asset_loader is None:
            return  # No scene manager wired (e.g. in tests)

        from src.assets.loader import AssetLoader
        from src.scenes.game import GameScene

        loader: AssetLoader = self._asset_loader
        categories = loader.categories()
        if not categories:
            return
        category = random.choice(categories)

        registry = self._registry
        sm = self._scene_manager
        sav = self._save_manager
        sett = self._settings
        aud = self._audio_manager

        game = GameScene(
            registry,
            self._selected_difficulty,
            category,
            loader,
            scene_manager=sm,
            save_manager=sav,
            settings=sett,
            audio_manager=aud,
            menu_factory=lambda: MenuScene(
                registry, scene_manager=sm, asset_loader=loader,
                save_manager=sav, settings=sett, audio_manager=aud,
            ),
        )
        sm.switch(game)  # type: ignore[union-attr]

    def update(self, dt: float) -> None:
        if self._error_timer > 0:
            self._error_timer -= dt
            if self._error_timer <= 0:
                self._error_message = ""

    def draw(self, surface: pygame.Surface) -> None:
        self._refresh_layout_if_needed(surface)
        theme: Theme = self._registry.active
        surface.fill(theme.background)

        title_rect = pygame.Rect(
            0, surface.get_height() // 10, surface.get_width(), surface.get_height() // 8
        )
        self._label.draw(surface, "Delicious Memory", title_rect, theme, style="title")

        # Difficulty label
        diff_label_rect = pygame.Rect(
            0,
            self._difficulty_buttons[0].rect.top - 36,
            surface.get_width(),
            30,
        )
        self._label.draw(surface, "Difficulty", diff_label_rect, theme, style="heading")

        for btn in self._difficulty_buttons:
            btn.draw(surface, theme)
        for btn in self._buttons:
            btn.draw(surface, theme)

        # Error message (AC-5.4)
        if self._error_message:
            err_rect = pygame.Rect(
                0, surface.get_height() - 60, surface.get_width(), 40
            )
            self._label.draw(surface, self._error_message, err_rect, theme, style="caption")
