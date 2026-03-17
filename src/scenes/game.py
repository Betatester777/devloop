# Implements: REQ-1 AC-1.1, AC-1.2, AC-1.3, AC-1.4 — Game scene with card grid
# Implements: REQ-4 AC-4.1, AC-4.3, AC-4.4, AC-4.5 — Scorer, timer, result screen
# Implements: REQ-5 AC-5.1, AC-5.2 — Save-and-quit and resume from state
# Implements: REQ-6 AC-6.2, AC-6.6 — Audio events and reduced animation
# See: ARC §src/scenes/game.py

from __future__ import annotations

import random

import pygame

from src.assets.loader import AssetLoader
from src.game.board import BOARD_SIZES, Board, Difficulty
from src.game.card import Card, CardState
from src.game.match_engine import GameEvent, MatchEngine
from src.game.scorer import Scorer
from src.scenes.base import Scene
from src.theme import Theme, ThemeRegistry
from src.ui import Button, Label

_CARD_GAP = 8
_CARD_BORDER = 3
_TOP_BAR_H = 60


class GameScene(Scene):
    """Renders the card grid, handles clicks/keyboard, and delegates to MatchEngine."""

    # Time limits per difficulty (seconds); None = untimed.
    _TIME_LIMITS: dict[Difficulty, float | None] = {
        Difficulty.EASY: None,
        Difficulty.NORMAL: 180.0,
        Difficulty.HARD: 300.0,
    }

    def __init__(
        self,
        theme_registry: ThemeRegistry,
        difficulty: Difficulty,
        category: str,
        asset_loader: AssetLoader,
        *,
        scene_manager: object | None = None,
        menu_factory: object | None = None,
        save_manager: object | None = None,
        settings: object | None = None,
        audio_manager: object | None = None,
        game_state: object | None = None,
    ) -> None:
        self._registry = theme_registry
        self._difficulty = difficulty
        self._category = category
        self._loader = asset_loader
        self._scene_manager = scene_manager
        self._menu_factory = menu_factory
        self._save_manager = save_manager
        self._settings = settings
        self._audio_manager = audio_manager
        self._label = Label()

        if game_state is not None:
            # Resume from saved state (AC-5.1, AC-5.2)
            from src.game.state import GameState
            gs: GameState = game_state  # type: ignore[assignment]
            self._board = gs.board
            self._scorer = gs.scorer
        else:
            # Build a fresh board
            cols, rows = BOARD_SIZES[difficulty]
            n_pairs = (cols * rows) // 2
            image_ids = self._loader.image_ids(category)
            chosen = random.sample(image_ids, n_pairs)
            self._board = Board.build(difficulty, category, chosen)
            self._scorer = Scorer(time_limit=self._TIME_LIMITS.get(difficulty))

        self._engine = MatchEngine()

        # Keyboard cursor
        self._cursor_col = 0
        self._cursor_row = 0

        # Layout state (recomputed on draw)
        self._card_rects: list[pygame.Rect] = []
        self._card_size: tuple[int, int] = (0, 0)
        self._last_surface_size: tuple[int, int] = (0, 0)

        # Back button
        self._back_btn = Button(pygame.Rect(10, 10, 100, 40), "Menu")

        # Win banner timer
        self._win_timer: float = 0.0
        self._game_won: bool = False

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _compute_layout(self, surface: pygame.Surface) -> None:
        """Recompute card rects when the surface size changes."""
        sw, sh = surface.get_size()
        if (sw, sh) == self._last_surface_size:
            return
        self._last_surface_size = (sw, sh)

        cols = self._board.cols
        rows = self._board.rows
        avail_w = sw - _CARD_GAP * (cols + 1)
        avail_h = sh - _TOP_BAR_H - _CARD_GAP * (rows + 1)
        card_w = max(40, avail_w // cols)
        card_h = max(40, avail_h // rows)
        # Keep cards square
        side = min(card_w, card_h)
        self._card_size = (side, side)

        total_w = cols * side + (cols - 1) * _CARD_GAP
        total_h = rows * side + (rows - 1) * _CARD_GAP
        x0 = (sw - total_w) // 2
        y0 = _TOP_BAR_H + (sh - _TOP_BAR_H - total_h) // 2

        self._card_rects = []
        for r in range(rows):
            for c in range(cols):
                x = x0 + c * (side + _CARD_GAP)
                y = y0 + r * (side + _CARD_GAP)
                self._card_rects.append(pygame.Rect(x, y, side, side))

        # Reposition back button
        self._back_btn.rect = pygame.Rect(10, 10, 100, 40)

    def _card_index_at_pos(self, pos: tuple[int, int]) -> int | None:
        for i, rect in enumerate(self._card_rects):
            if rect.collidepoint(pos):
                return i
        return None

    # ------------------------------------------------------------------
    # Scene interface
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._back_btn.contains(event.pos):
                self._go_back()
                return
            idx = self._card_index_at_pos(event.pos)
            if idx is not None and not self._game_won:
                self._play_sound_event("flip")
                self._engine.flip(self._board.cards[idx])

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_back()
                return
            if self._game_won:
                return
            self._handle_keyboard(event)

    def _handle_keyboard(self, event: pygame.event.Event) -> None:
        cols = self._board.cols
        rows = self._board.rows

        if event.key == pygame.K_LEFT:
            self._cursor_col = (self._cursor_col - 1) % cols
        elif event.key == pygame.K_RIGHT:
            self._cursor_col = (self._cursor_col + 1) % cols
        elif event.key == pygame.K_UP:
            self._cursor_row = (self._cursor_row - 1) % rows
        elif event.key == pygame.K_DOWN:
            self._cursor_row = (self._cursor_row + 1) % rows
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            idx = self._cursor_row * cols + self._cursor_col
            self._play_sound_event("flip")
            self._engine.flip(self._board.cards[idx])

    def update(self, dt: float) -> None:
        if self._game_won:
            self._win_timer += dt
            return

        event = self._engine.update(dt, self._board.cards)

        # Record moves on match or mismatch (AC-4.1)
        if event in (GameEvent.MATCH, GameEvent.MISMATCH, GameEvent.BOARD_CLEAR):
            self._scorer.record_move()

        # Audio feedback (AC-6.2)
        if event == GameEvent.MATCH:
            self._play_sound_event("match")
        elif event == GameEvent.MISMATCH:
            self._play_sound_event("mismatch")

        # Advance timer (AC-4.3)
        time_expired = self._scorer.update(dt)

        if event == GameEvent.BOARD_CLEAR:
            self._game_won = True
            self._play_sound_event("win")
            self._delete_save()
            self._show_result(won=True)
            return

        if time_expired:
            self._game_won = True
            self._play_sound_event("lose")
            self._delete_save()
            self._show_result(won=False)

    def draw(self, surface: pygame.Surface) -> None:
        self._compute_layout(surface)
        theme: Theme = self._registry.active
        surface.fill(theme.background)

        # Top bar
        self._back_btn.draw(surface, theme)
        sw = surface.get_width()
        diff_label = self._difficulty.value.capitalize()
        cat_label = self._category.replace("_", " ").title()
        info_rect = pygame.Rect(120, 5, sw - 240, 25)
        self._label.draw(surface, f"{cat_label} — {diff_label}", info_rect, theme, style="caption")

        # HUD: moves and timer
        hud_rect = pygame.Rect(120, 30, sw - 240, 25)
        hud_parts = [f"Moves: {self._scorer.moves}"]
        if self._scorer.time_remaining is not None:
            rem = max(0.0, self._scorer.time_remaining)
            mins, secs = int(rem // 60), int(rem % 60)
            hud_parts.append(f"Time: {mins}:{secs:02d}")
        else:
            elapsed = self._scorer.elapsed_seconds
            mins, secs = int(elapsed // 60), int(elapsed % 60)
            hud_parts.append(f"Time: {mins}:{secs:02d}")
        self._label.draw(surface, "   ".join(hud_parts), hud_rect, theme, style="caption")

        # Draw cards
        for i, card in enumerate(self._board.cards):
            rect = self._card_rects[i]
            self._draw_card(surface, card, rect, theme)

        # Keyboard cursor highlight
        if not self._game_won:
            cursor_idx = self._cursor_row * self._board.cols + self._cursor_col
            if 0 <= cursor_idx < len(self._card_rects):
                cursor_rect = self._card_rects[cursor_idx].inflate(6, 6)
                pygame.draw.rect(surface, theme.focus_ring, cursor_rect, width=3, border_radius=4)

        # Win message
        if self._game_won:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))
            win_rect = pygame.Rect(0, surface.get_height() // 3, surface.get_width(), 100)
            self._label.draw(surface, "You Win!", win_rect, theme, style="title")

    def _draw_card(
        self, surface: pygame.Surface, card: Card, rect: pygame.Rect, theme: Theme
    ) -> None:
        """Draw a single card with flip animation based on flip_progress."""
        progress = card.flip_progress

        if card.state == CardState.MATCHED:
            # Matched cards: show face with muted border
            self._draw_card_face(surface, card, rect, theme, alpha=180)
            return

        if progress <= 0.0:
            # Fully face-down: draw card back
            pygame.draw.rect(surface, theme.card_back, rect, border_radius=6)
            pygame.draw.rect(surface, theme.surface, rect, width=2, border_radius=6)
            return

        if progress >= 1.0:
            # Fully face-up: draw card face
            self._draw_card_face(surface, card, rect, theme)
            return

        # Reduced animation mode: skip flip animation (AC-6.6)
        if self._reduced_animation:
            if card.state in (CardState.FLIPPING_UP, CardState.FACE_UP):
                self._draw_card_face(surface, card, rect, theme)
            else:
                pygame.draw.rect(surface, theme.card_back, rect, border_radius=6)
                pygame.draw.rect(surface, theme.surface, rect, width=2, border_radius=6)
            return

        # Mid-flip: scale width based on progress to simulate 3D flip
        if progress < 0.5:
            # Showing back side, shrinking
            scale = 1.0 - progress * 2  # 1.0 → 0.0
            w = max(2, int(rect.width * scale))
            shrunk = pygame.Rect(rect.centerx - w // 2, rect.y, w, rect.height)
            pygame.draw.rect(surface, theme.card_back, shrunk, border_radius=4)
        else:
            # Showing front side, growing
            scale = (progress - 0.5) * 2  # 0.0 → 1.0
            w = max(2, int(rect.width * scale))
            shrunk = pygame.Rect(rect.centerx - w // 2, rect.y, w, rect.height)
            self._draw_card_face(surface, card, shrunk, theme)

    def _draw_card_face(
        self,
        surface: pygame.Surface,
        card: Card,
        rect: pygame.Rect,
        theme: Theme,
        alpha: int = 255,
    ) -> None:
        """Draw the face of a card (image + border)."""
        pygame.draw.rect(surface, theme.card_front_border, rect, border_radius=6)
        inner = rect.inflate(-_CARD_BORDER * 2, -_CARD_BORDER * 2)
        pygame.draw.rect(surface, (255, 255, 255), inner, border_radius=4)

        if inner.width > 4 and inner.height > 4:
            try:
                img = self._loader.get_image_scaled(
                    self._category, card.image_id, (inner.width, inner.height)
                )
                if alpha < 255:
                    img = img.copy()
                    img.set_alpha(alpha)
                surface.blit(img, inner.topleft)
            except FileNotFoundError:
                # Fallback: just show the border
                pass

    def _show_result(self, *, won: bool) -> None:
        """Transition to the result screen."""
        if self._scene_manager is None or self._menu_factory is None:
            return
        from src.scenes.results import Outcome, OutcomeKind, ResultScene

        n_pairs = (self._board.cols * self._board.rows) // 2
        pairs_found = sum(
            1 for c in self._board.cards if c.state == CardState.MATCHED
        ) // 2
        score = self._scorer.compute_score(pairs_found)

        outcome = Outcome(
            kind=OutcomeKind.WIN if won else OutcomeKind.LOSS,
            score=score,
            moves=self._scorer.moves,
            elapsed_seconds=self._scorer.elapsed_seconds,
            pairs_found=pairs_found,
            total_pairs=n_pairs,
        )

        sm = self._scene_manager
        reg = self._registry
        diff = self._difficulty
        cat = self._category
        loader = self._loader
        mf = self._menu_factory
        sav = self._save_manager
        sett = self._settings
        aud = self._audio_manager

        self._scene_manager.switch(  # type: ignore[union-attr]
            ResultScene(
                reg,
                outcome,
                scene_manager=sm,
                play_again_factory=lambda: GameScene(
                    reg, diff, cat, loader, scene_manager=sm, menu_factory=mf,
                    save_manager=sav, settings=sett, audio_manager=aud,
                ),
                menu_factory=mf,
            )
        )

    def _go_back(self) -> None:
        """Save state and return to menu scene (AC-5.1)."""
        self._save_current_state()
        if self._scene_manager is not None and self._menu_factory is not None:
            self._scene_manager.switch(self._menu_factory())

    def _save_current_state(self) -> None:
        """Persist the current game state via SaveManager."""
        if self._save_manager is None:
            return
        from src.game.state import GameState

        state = GameState(
            board=self._board,
            scorer=self._scorer,
            category=self._category,
            difficulty=self._difficulty,
        )
        self._save_manager.save(state)

    def _delete_save(self) -> None:
        """Remove save file after game completion."""
        if self._save_manager is not None:
            self._save_manager.delete()

    def _play_sound_event(self, name: str) -> None:
        """Play a sound effect via AudioManager (AC-6.2)."""
        if self._audio_manager is None:
            return
        from src.audio import SoundEvent

        mapping = {
            "flip": SoundEvent.FLIP,
            "match": SoundEvent.MATCH,
            "mismatch": SoundEvent.MISMATCH,
            "win": SoundEvent.WIN,
            "lose": SoundEvent.LOSE,
        }
        se = mapping.get(name)
        if se is not None:
            self._audio_manager.play(se)

    @property
    def _reduced_animation(self) -> bool:
        """True when reduced animation mode is active (AC-6.6)."""
        if self._settings is None:
            return False
        return self._settings.animation_mode == "reduced"
