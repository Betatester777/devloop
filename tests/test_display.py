# Verifies: AC-1.2, AC-1.3 — Display scaling and resize behaviour
from __future__ import annotations

import os

import pygame
import pytest

# Force headless rendering for CI / test environments
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialized (and quit afterwards) for every test."""
    pygame.init()
    yield
    pygame.quit()


# Import *after* env var is set so Display uses the dummy driver
from src.display import Display  # noqa: E402


class TestScaleRect:
    def test_identity_at_default_size(self) -> None:
        d = Display(title="Test", default_size=(1024, 768))
        base = pygame.Rect(100, 200, 300, 400)
        scaled = d.scale_rect(base)
        assert scaled == base

    def test_proportional_scaling_double(self) -> None:
        d = Display(title="Test", default_size=(1024, 768))
        d.handle_resize(2048, 1536)
        base = pygame.Rect(100, 100, 200, 200)
        scaled = d.scale_rect(base)
        assert scaled.x == 200
        assert scaled.y == 200
        assert scaled.width == 400
        assert scaled.height == 400

    def test_proportional_scaling_half(self) -> None:
        d = Display(title="Test", default_size=(1024, 768))
        d.handle_resize(512, 384)
        base = pygame.Rect(0, 0, 1024, 768)
        scaled = d.scale_rect(base)
        assert scaled.width == 512
        assert scaled.height == 384


class TestLogicalSize:
    def test_initial_size(self) -> None:
        d = Display(title="Test", default_size=(1024, 768))
        assert d.logical_size() == (1024, 768)

    def test_size_after_resize(self) -> None:
        d = Display(title="Test", default_size=(1024, 768))
        d.handle_resize(800, 600)
        assert d.logical_size() == (800, 600)

    def test_minimum_size_enforced(self) -> None:
        d = Display(title="Test", default_size=(1024, 768))
        d.handle_resize(100, 50)
        w, h = d.logical_size()
        assert w >= 320
        assert h >= 240
