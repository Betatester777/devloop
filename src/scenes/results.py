# Implements: REQ-4 AC-4.4, AC-4.5 — Victory / game-over results screen
# See: ARC §src/scenes/results.py

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import pygame

from src.scenes.base import Scene
from src.theme import Theme, ThemeRegistry
from src.ui import Button, FocusGroup, Label


class OutcomeKind(Enum):
    WIN = "win"
    LOSS = "loss"


@dataclass
class Outcome:
    """Data shown on the results screen."""

    kind: OutcomeKind
    score: int
    moves: int
    elapsed_seconds: float
    pairs_found: int
    total_pairs: int


class ResultScene(Scene):
    """Displays the round outcome with score, moves, and elapsed time (AC-4.5).

    Offers *Play Again* and *Main Menu* actions.
    """

    def __init__(
        self,
        theme_registry: ThemeRegistry,
        outcome: Outcome,
        *,
        scene_manager: object | None = None,
        play_again_factory: object | None = None,
        menu_factory: object | None = None,
    ) -> None:
        self._registry = theme_registry
        self.outcome = outcome
        self._scene_manager = scene_manager
        self._play_again_factory = play_again_factory
        self._menu_factory = menu_factory
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
        btn_w = max(200, bounds.width // 4)
        btn_h = max(48, bounds.height // 10)
        gap = max(12, btn_h // 3)
        start_y = bounds.centery + bounds.height // 6

        labels = ["Play Again", "Main Menu"]
        self._buttons = [
            Button(
                pygame.Rect(cx - btn_w // 2, start_y + i * (btn_h + gap), btn_w, btn_h),
                lbl,
            )
            for i, lbl in enumerate(labels)
        ]
        self._focus = FocusGroup()
        for btn in self._buttons:
            self._focus.add(btn)

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

        if activated is not None:
            self._activate(activated.label)

    def _activate(self, label: str) -> None:
        if label == "Play Again" and self._scene_manager and self._play_again_factory:
            self._scene_manager.switch(self._play_again_factory())  # type: ignore[union-attr]
        elif label == "Main Menu" and self._scene_manager and self._menu_factory:
            self._scene_manager.switch(self._menu_factory())  # type: ignore[union-attr]

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self._refresh_layout_if_needed(surface)
        theme: Theme = self._registry.active
        surface.fill(theme.background)

        sw = surface.get_width()
        o = self.outcome

        # Title
        title_text = "You Win!" if o.kind == OutcomeKind.WIN else "Time's Up!"
        title_rect = pygame.Rect(0, surface.get_height() // 10, sw, 80)
        self._label.draw(surface, title_text, title_rect, theme, style="title")

        # Stats (AC-4.5: score, moves, elapsed time)
        line_h = 40
        base_y = surface.get_height() // 4

        stats = [
            f"Score: {o.score}",
            f"Moves: {o.moves}",
            f"Time: {int(o.elapsed_seconds // 60)}:{int(o.elapsed_seconds % 60):02d}",
            f"Pairs: {o.pairs_found} / {o.total_pairs}",
        ]
        for i, text in enumerate(stats):
            r = pygame.Rect(0, base_y + i * line_h, sw, line_h)
            self._label.draw(surface, text, r, theme, style="heading")

        # Buttons
        for btn in self._buttons:
            btn.draw(surface, theme)
