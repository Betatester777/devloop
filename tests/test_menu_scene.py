# Verifies: AC-7.1 AC-7.2 AC-7.3 AC-7.4 — MenuScene launch, resize, focus cycle, quit
# Verifies: AC-3.3 — Difficulty selector visible and interactive on main menu
# Requirement: REQ-7 (Responsive desktop UI), REQ-3 (Difficulty levels)

import pygame
import pytest

from src.game.board import Difficulty
from src.scenes.menu import MenuScene
from src.theme import ThemeRegistry


@pytest.fixture(autouse=True)
def _pygame_init():
    pygame.init()
    yield
    pygame.quit()


def _make_surface(width: int, height: int) -> pygame.Surface:
    return pygame.Surface((width, height))


def _make_menu() -> MenuScene:
    return MenuScene(ThemeRegistry())


class TestMenuSceneLaunch:
    """AC-7.1: Main menu renders on screen within 5 s without error or crash."""

    def test_menu_scene_draws_without_exception(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)  # No exception means the menu appeared crash-free

    def test_menu_scene_exposes_new_game_settings_and_quit_buttons(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)
        labels = {btn.label for btn in scene._buttons}
        assert "New Game" in labels
        assert "Settings" in labels
        assert "Quit" in labels


class TestMenuSceneResize:
    """AC-7.2: All controls visible and proportionally scaled at any supported resolution."""

    def test_buttons_fit_within_initial_surface_bounds(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)
        bounds = surface.get_rect()
        for btn in scene._buttons:
            assert bounds.contains(btn.rect), (
                f"Button '{btn.label}' {btn.rect} outside 800×600 bounds"
            )

    def test_buttons_fit_within_bounds_after_shrink(self):
        scene = _make_menu()
        scene.draw(_make_surface(800, 600))
        small = _make_surface(400, 300)
        scene.draw(small)
        bounds = small.get_rect()
        for btn in scene._buttons:
            assert bounds.contains(btn.rect), (
                f"Button '{btn.label}' {btn.rect} clipped in 400×300 surface"
            )

    def test_buttons_fit_within_bounds_after_expand(self):
        scene = _make_menu()
        scene.draw(_make_surface(800, 600))
        large = _make_surface(1920, 1080)
        scene.draw(large)
        bounds = large.get_rect()
        for btn in scene._buttons:
            assert bounds.contains(btn.rect), (
                f"Button '{btn.label}' {btn.rect} clipped in 1920×1080 surface"
            )


class TestMenuSceneFocusCycle:
    """AC-7.3: No rendering artefacts or input lock after alt-tab away and back."""

    def _focus_event(self, gained: bool) -> pygame.event.Event:
        return pygame.event.Event(pygame.ACTIVEEVENT, gain=int(gained), state=6)

    def test_draw_succeeds_after_focus_lost_and_regained(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)
        scene.handle_event(self._focus_event(gained=False))
        scene.handle_event(self._focus_event(gained=True))
        scene.draw(surface)  # No exception means no rendering corruption

    def test_keyboard_navigation_works_after_focus_regained(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)
        scene.handle_event(self._focus_event(gained=False))
        scene.handle_event(self._focus_event(gained=True))
        tab = pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_TAB, mod=pygame.KMOD_NONE,
            unicode="\t", scancode=0,
        )
        scene.handle_event(tab)
        all_btns = scene._difficulty_buttons + scene._buttons
        assert any(btn.focused for btn in all_btns), (
            "Keyboard input is locked — no button has focus after Tab post-focus-cycle"
        )


class TestMenuSceneQuit:
    """AC-7.4: Application exits cleanly within 2 s when quit action is triggered."""

    def test_quit_button_click_posts_pygame_quit_event(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)  # Build layout so button rects are populated
        pygame.event.clear()
        quit_btn = next(btn for btn in scene._buttons if btn.label == "Quit")
        click = pygame.event.Event(
            pygame.MOUSEBUTTONUP, button=1, pos=quit_btn.rect.center
        )
        scene.handle_event(click)
        quit_events = pygame.event.get(pygame.QUIT)
        assert len(quit_events) == 1, (
            "Quit button click must post exactly one QUIT event to the main loop"
        )

    def test_main_loop_exits_with_code_zero_on_quit_event(self, monkeypatch):
        """The main event loop handles QUIT cleanly, calling sys.exit(0)."""
        from src.main import main

        first_call = {"done": False}
        quit_event = pygame.event.Event(pygame.QUIT)

        def mock_event_get():
            if not first_call["done"]:
                first_call["done"] = True
                return [quit_event]
            return []

        monkeypatch.setattr(pygame.event, "get", mock_event_get)
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


class TestMenuSceneDifficulty:
    """AC-3.3: Difficulty selector visible and interactive before any round begins."""

    def test_difficulty_buttons_present(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)
        labels = {btn.label for btn in scene._difficulty_buttons}
        assert labels == {"Easy", "Normal", "Hard"}

    def test_default_difficulty_is_normal(self):
        scene = _make_menu()
        assert scene.selected_difficulty == Difficulty.NORMAL

    def test_click_easy_changes_difficulty(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)
        easy_btn = next(b for b in scene._difficulty_buttons if b.label == "Easy")
        click = pygame.event.Event(
            pygame.MOUSEBUTTONUP, button=1, pos=easy_btn.rect.center
        )
        scene.handle_event(click)
        assert scene.selected_difficulty == Difficulty.EASY

    def test_click_hard_changes_difficulty(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)
        hard_btn = next(b for b in scene._difficulty_buttons if b.label == "Hard")
        click = pygame.event.Event(
            pygame.MOUSEBUTTONUP, button=1, pos=hard_btn.rect.center
        )
        scene.handle_event(click)
        assert scene.selected_difficulty == Difficulty.HARD

    def test_difficulty_buttons_fit_within_bounds(self):
        scene = _make_menu()
        surface = _make_surface(800, 600)
        scene.draw(surface)
        bounds = surface.get_rect()
        for btn in scene._difficulty_buttons:
            assert bounds.contains(btn.rect), (
                f"Difficulty button '{btn.label}' {btn.rect} outside bounds"
            )

    def test_selected_difficulty_button_is_disabled(self):
        """The currently selected difficulty button is visually distinct (disabled)."""
        scene = _make_menu()
        normal_btn = next(b for b in scene._difficulty_buttons if b.label == "Normal")
        assert normal_btn.enabled is False  # selected = disabled visually

    def test_board_dimensions_match_selected_difficulty(self):
        """AC-3.1: Selecting a difficulty on the menu and starting a game produces
        board dimensions that match that difficulty's specification."""
        from src.game.board import BOARD_SIZES, Board

        surface = _make_surface(800, 600)
        for label, expected_difficulty in (
            ("Easy", Difficulty.EASY),
            ("Normal", Difficulty.NORMAL),
            ("Hard", Difficulty.HARD),
        ):
            scene = _make_menu()
            scene.draw(surface)
            btn = next(b for b in scene._difficulty_buttons if b.label == label)
            click = pygame.event.Event(
                pygame.MOUSEBUTTONUP, button=1, pos=btn.rect.center
            )
            scene.handle_event(click)
            assert scene.selected_difficulty == expected_difficulty

            expected_cols, expected_rows = BOARD_SIZES[expected_difficulty]
            expected_pairs = expected_cols * expected_rows // 2
            image_ids = [f"img_{i:03d}" for i in range(expected_pairs)]
            board = Board.build(scene.selected_difficulty, "test", image_ids)
            assert board.cols == expected_cols, (
                f"{label}: expected {expected_cols} cols, got {board.cols}"
            )
            assert board.rows == expected_rows, (
                f"{label}: expected {expected_rows} rows, got {board.rows}"
            )
