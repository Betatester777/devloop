# Verifies: AC-1.1 — Theme module returns correct instances and rejects unknown names
from __future__ import annotations

import pytest

from src.theme import (
    DARK_THEME,
    LIGHT_THEME,
    G500,
    G700,
    N100,
    N700,
    Theme,
    get_theme,
)


class TestGetTheme:
    def test_light_theme_returned(self) -> None:
        theme = get_theme("light")
        assert theme is LIGHT_THEME

    def test_dark_theme_returned(self) -> None:
        theme = get_theme("dark")
        assert theme is DARK_THEME

    def test_unknown_name_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unknown theme 'neon'"):
            get_theme("neon")


class TestThemeColors:
    """Sanity-check that themes use the expected palette values."""

    def test_light_theme_is_frozen_dataclass(self) -> None:
        assert isinstance(LIGHT_THEME, Theme)
        with pytest.raises(AttributeError):
            LIGHT_THEME.name = "modified"  # type: ignore[misc]

    def test_light_theme_uses_brand_colors(self) -> None:
        assert LIGHT_THEME.background == N100
        assert LIGHT_THEME.text_primary == N700
        assert LIGHT_THEME.accent == G500
        assert LIGHT_THEME.card_back == G700

    def test_dark_theme_uses_brand_colors(self) -> None:
        assert DARK_THEME.background == N700
        assert DARK_THEME.text_primary == N100

    def test_color_tuples_are_valid_rgb(self) -> None:
        for theme in (LIGHT_THEME, DARK_THEME):
            for field_name in (
                "background",
                "card_back",
                "card_face",
                "text_primary",
                "text_secondary",
                "accent",
                "focus_indicator",
                "button_bg",
                "button_text",
                "timer_bar",
                "success",
                "failure",
            ):
                color = getattr(theme, field_name)
                assert isinstance(color, tuple) and len(color) == 3
                assert all(0 <= c <= 255 for c in color), f"{field_name}={color}"
