# Implements: REQ-2 AC-2.1 through AC-2.5 — Game board screen with card interaction
# See: ARC §4 (screens), §5 (board), §6 (card_animator)
from __future__ import annotations

import pygame

from ..board import Board, Card, CardState, FlipResult, MatchResult
from ..card_animator import CardAnimator
from ..display import Display
from ..screens import ScreenAction
from ..theme import Theme


class GameScreen:
    """Renders the card grid and coordinates Board + CardAnimator."""

    _CARD_GAP = 10
    _TOP_MARGIN = 80

    def __init__(
        self,
        board: Board,
        animator: CardAnimator,
        display: Display,
        theme: Theme,
        card_surfaces: dict[str, pygame.Surface],
        card_back: pygame.Surface,
    ) -> None:
        self._board = board
        self._animator = animator
        self._display = display
        self._theme = theme
        self._card_surfaces = card_surfaces
        self._card_back = card_back
        # Keyboard cursor position
        self._cursor_row = 0
        self._cursor_col = 0
        # Track two flipped cards for mismatch delay
        self._pending_pair: tuple[int, int, int, int] | None = None

    # ------------------------------------------------------------------
    # Screen protocol
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None:
        # AC-2.5: ignore all card input during animation
        if self._animator.is_animating():
            # Still allow escape even during animation
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return ScreenAction(action="main_menu")
            return None

        if event.type == pygame.KEYDOWN:
            return self._handle_key(event.key)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_click(event.pos)

        return None

    def update(self, dt_ms: float) -> None:
        events = self._animator.update(dt_ms)
        # Sync animation lock with animator state
        if self._animator.is_animating():
            self._board.set_animation_lock()
        else:
            self._board.clear_animation_lock()

        for anim_event in events:
            if anim_event.kind == "flip_complete":
                self._on_flip_complete()
            elif anim_event.kind == "mismatch_delay_complete":
                self._on_mismatch_delay_complete()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self._theme.background)
        w, h = self._display.logical_size()
        rows, cols = self._board.rows, self._board.cols

        # Calculate card size to fit the window
        card_w, card_h = self._card_layout(w, h, rows, cols)

        # Grid offset to center
        grid_w = cols * card_w + (cols - 1) * self._CARD_GAP
        grid_h = rows * card_h + (rows - 1) * self._CARD_GAP
        ox = (w - grid_w) // 2
        oy = self._TOP_MARGIN + (h - self._TOP_MARGIN - grid_h) // 2

        for card in self._board.all_cards():
            r, c = card.grid_pos
            x = ox + c * (card_w + self._CARD_GAP)
            y = oy + r * (card_h + self._CARD_GAP)
            rect = pygame.Rect(x, y, card_w, card_h)

            progress = self._animator.flip_progress(r, c)
            self._draw_card(surface, rect, card, progress)

            # Cursor indicator
            if r == self._cursor_row and c == self._cursor_col:
                indicator = rect.inflate(6, 6)
                pygame.draw.rect(surface, self._theme.focus_indicator, indicator, 3)

        # Header
        font = pygame.font.SysFont(None, 32)
        pairs_text = f"Pairs: {self._board.matched_count()}/{self._board.total_pairs()}"
        text_surf = font.render(pairs_text, True, self._theme.text_primary)
        surface.blit(text_surf, (20, 20))

    # ------------------------------------------------------------------
    # Internal: input handling
    # ------------------------------------------------------------------

    def _handle_key(self, key: int) -> ScreenAction | None:
        if key == pygame.K_ESCAPE:
            return ScreenAction(action="main_menu")

        if key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            self._move_cursor(key)
            return None

        if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            return self._try_flip(self._cursor_row, self._cursor_col)

        return None

    def _handle_click(self, pos: tuple[int, int]) -> ScreenAction | None:
        w, h = self._display.logical_size()
        rows, cols = self._board.rows, self._board.cols
        card_w, card_h = self._card_layout(w, h, rows, cols)
        grid_w = cols * card_w + (cols - 1) * self._CARD_GAP
        grid_h = rows * card_h + (rows - 1) * self._CARD_GAP
        ox = (w - grid_w) // 2
        oy = self._TOP_MARGIN + (h - self._TOP_MARGIN - grid_h) // 2

        mx, my = pos
        for card in self._board.all_cards():
            r, c = card.grid_pos
            x = ox + c * (card_w + self._CARD_GAP)
            y = oy + r * (card_h + self._CARD_GAP)
            rect = pygame.Rect(x, y, card_w, card_h)
            if rect.collidepoint(mx, my):
                self._cursor_row, self._cursor_col = r, c
                return self._try_flip(r, c)
        return None

    def _try_flip(self, row: int, col: int) -> ScreenAction | None:
        result = self._board.flip_card(row, col)
        if result is FlipResult.FLIPPED:
            self._animator.start_flip(row, col)
        return None

    def _move_cursor(self, key: int) -> None:
        if key == pygame.K_UP:
            self._cursor_row = (self._cursor_row - 1) % self._board.rows
        elif key == pygame.K_DOWN:
            self._cursor_row = (self._cursor_row + 1) % self._board.rows
        elif key == pygame.K_LEFT:
            self._cursor_col = (self._cursor_col - 1) % self._board.cols
        elif key == pygame.K_RIGHT:
            self._cursor_col = (self._cursor_col + 1) % self._board.cols

    # ------------------------------------------------------------------
    # Internal: animation callbacks
    # ------------------------------------------------------------------

    def _on_flip_complete(self) -> None:
        match_result = self._board.evaluate_pair()
        if match_result is MatchResult.MATCH:
            # AC-2.3: both cards stay revealed
            face_up = [c for c in self._board.all_cards() if c.state is CardState.FACE_UP]
            self._board.commit_match()
            if self._board.is_complete():
                # Temporary: return to main menu (victory screen is REQ-5)
                pass  # handled in update via ScreenAction
        elif match_result is MatchResult.MISMATCH:
            # AC-2.4: flip back after delay
            face_up = [c for c in self._board.all_cards() if c.state is CardState.FACE_UP]
            if len(face_up) == 2:
                r1, c1 = face_up[0].grid_pos
                r2, c2 = face_up[1].grid_pos
                self._pending_pair = (r1, c1, r2, c2)
                self._animator.start_mismatch_delay(r1, c1, r2, c2)

    def _on_mismatch_delay_complete(self) -> None:
        # AC-2.4: flip mismatched pair back
        self._board.reset_pair()
        self._pending_pair = None

    # ------------------------------------------------------------------
    # Internal: rendering
    # ------------------------------------------------------------------

    def _card_layout(self, win_w: int, win_h: int, rows: int, cols: int) -> tuple[int, int]:
        """Calculate card pixel size to fit the window."""
        avail_w = win_w - 40  # side margins
        avail_h = win_h - self._TOP_MARGIN - 40
        card_w = (avail_w - (cols - 1) * self._CARD_GAP) // cols
        card_h = (avail_h - (rows - 1) * self._CARD_GAP) // rows
        # Square cards: use the smaller dimension
        side = min(card_w, card_h)
        return max(side, 30), max(side, 30)

    def _draw_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        card: Card,
        progress: float,
    ) -> None:
        # Flip animation: squeeze horizontally at midpoint
        if progress < 1.0:
            # First half: squeezing face-down; second half: expanding face-up
            scale = abs(2.0 * progress - 1.0)
            draw_w = max(int(rect.width * scale), 2)
            draw_rect = pygame.Rect(
                rect.centerx - draw_w // 2, rect.y, draw_w, rect.height
            )
            showing_face = progress > 0.5
        else:
            draw_rect = rect
            showing_face = card.state in (CardState.FACE_UP, CardState.MATCHED)

        if showing_face:
            # Draw card face
            face_surf = self._card_surfaces.get(card.image_id)
            if face_surf:
                scaled = pygame.transform.scale(face_surf, (draw_rect.width, draw_rect.height))
                surface.blit(scaled, draw_rect)
            else:
                pygame.draw.rect(surface, self._theme.card_face, draw_rect, border_radius=6)
            if card.state is CardState.MATCHED:
                # Dim matched cards slightly
                overlay = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 60))
                surface.blit(overlay, draw_rect)
        else:
            # Draw card back
            scaled_back = pygame.transform.scale(self._card_back, (draw_rect.width, draw_rect.height))
            surface.blit(scaled_back, draw_rect)

        # Card border
        pygame.draw.rect(surface, self._theme.text_secondary, draw_rect, 1, border_radius=6)
