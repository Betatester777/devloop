# Implements: REQ-1 AC-1.1, AC-1.2, REQ-4 AC-4.1 — Main menu with difficulty selection
# See: ARC §4 (screens), ADR-2 (Board Sizes Per Difficulty)
from __future__ import annotations

import pygame

from ..display import Display
from ..focus_manager import FocusAction, FocusElement, FocusManager
from ..screens import ScreenAction
from ..theme import Theme


class MainMenuScreen:
    """Main menu with difficulty selection, Continue, Settings, and Quit."""

    # Design-space layout constants (will be scaled via Display.scale_rect)
    _TITLE_Y = 100
    _SUBTITLE_Y = 180
    _BUTTON_WIDTH = 300
    _BUTTON_HEIGHT = 56
    _BUTTON_GAP = 20
    _FIRST_BUTTON_Y = 230

    # Difficulty buttons first, then Continue / Settings / Quit
    _BUTTON_DEFS: list[tuple[str, str, dict]] = [
        ("Easy (3\u00d74)", "start_game", {"difficulty": "easy"}),
        ("Normal (4\u00d75)", "start_game", {"difficulty": "normal"}),
        ("Hard (5\u00d76)", "start_game", {"difficulty": "hard"}),
        ("Continue", "continue_game", {}),
        ("Settings", "open_settings", {}),
        ("Quit", "quit", {}),
    ]

    def __init__(
        self,
        display: Display,
        save_exists: bool,
        theme: Theme,
    ) -> None:
        self._display = display
        self._save_exists = save_exists
        self._theme = theme

        # Build focus elements in design-space
        self._focus_elements: list[FocusElement] = []
        for idx, (label, _action, _payload) in enumerate(self._BUTTON_DEFS):
            x = (display.design_width - self._BUTTON_WIDTH) // 2
            y = self._FIRST_BUTTON_Y + idx * (self._BUTTON_HEIGHT + self._BUTTON_GAP)
            selectable = True
            if label == "Continue" and not save_exists:
                selectable = False
            self._focus_elements.append(
                FocusElement(
                    name=label,
                    rect=pygame.Rect(x, y, self._BUTTON_WIDTH, self._BUTTON_HEIGHT),
                    selectable=selectable,
                )
            )

        self._focus_mgr = FocusManager(self._focus_elements)

    # ------------------------------------------------------------------
    # Screen protocol
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None:
        if event.type == pygame.KEYDOWN:
            action = self._focus_mgr.handle_key(event.key)
            if action is FocusAction.ACTIVATE:
                return self._activate_focused()
            if action is FocusAction.CANCEL:
                return ScreenAction(action="quit")
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_click(event.pos)

        return None

    def update(self, dt_ms: float) -> None:
        pass  # No animations on the menu yet

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self._theme.background)

        # Title
        title_font = pygame.font.SysFont(None, 64)
        title_surf = title_font.render("Delicious Memory", True, self._theme.text_primary)
        title_rect = title_surf.get_rect(
            centerx=surface.get_width() // 2,
            y=self._display.scale_rect(
                pygame.Rect(0, self._TITLE_Y, 0, 0)
            ).y,
        )
        surface.blit(title_surf, title_rect)

        # Subtitle — "Choose difficulty"
        sub_font = pygame.font.SysFont(None, 30)
        sub_surf = sub_font.render("Choose difficulty:", True, self._theme.text_secondary)
        sub_rect = sub_surf.get_rect(
            centerx=surface.get_width() // 2,
            y=self._display.scale_rect(
                pygame.Rect(0, self._SUBTITLE_Y, 0, 0)
            ).y,
        )
        surface.blit(sub_surf, sub_rect)

        # Buttons
        btn_font = pygame.font.SysFont(None, 36)
        focused_idx = self._focus_mgr.focused_index()

        for idx, (elem, (label, _action, _payload)) in enumerate(
            zip(self._focus_elements, self._BUTTON_DEFS)
        ):
            scaled = self._display.scale_rect(elem.rect)
            disabled = not elem.selectable

            # Background
            if disabled:
                bg_color = self._theme.text_secondary
            else:
                bg_color = self._theme.button_bg
            pygame.draw.rect(surface, bg_color, scaled, border_radius=8)

            # Label
            text_color = self._theme.button_text if not disabled else self._theme.background
            text_surf = btn_font.render(label, True, text_color)
            text_rect = text_surf.get_rect(center=scaled.center)
            surface.blit(text_surf, text_rect)

            # Focus indicator
            if idx == focused_idx:
                indicator_rect = scaled.inflate(8, 8)
                self._focus_mgr.draw_indicator(
                    surface, indicator_rect, self._theme.focus_indicator
                )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _activate_focused(self) -> ScreenAction | None:
        elem = self._focus_mgr.focused_element()
        if not elem.selectable:
            return None
        idx = self._focus_mgr.focused_index()
        _, action_str, payload = self._BUTTON_DEFS[idx]
        return ScreenAction(action=action_str, payload=payload)

    def _handle_click(self, pos: tuple[int, int]) -> ScreenAction | None:
        for idx, (elem, (_label, action_str, payload)) in enumerate(
            zip(self._focus_elements, self._BUTTON_DEFS)
        ):
            scaled = self._display.scale_rect(elem.rect)
            if scaled.collidepoint(pos) and elem.selectable:
                self._focus_mgr.set_focus(idx)
                return ScreenAction(action=action_str, payload=payload)
        return None
