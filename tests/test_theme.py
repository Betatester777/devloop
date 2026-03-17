# Verifies: AC-7.1 — palette tokens valid, THEMES dict present, ThemeRegistry.set_theme
# Requirement: REQ-7 (Responsive desktop UI)

import src.theme as theme_module
from src.theme import THEMES, ThemeRegistry

_PALETTE_TOKENS = [
    "G900", "G800", "G700", "G600", "G500", "G400", "G300", "G200", "G100",
    "G20", "G15",
    "N100", "N100Bold", "N100Bolder",
    "N200", "N200Bold", "N200Bolder",
    "N300", "N400", "N500", "N600", "N700",
]


def test_all_palette_tokens_are_rgb_triples():
    for token in _PALETTE_TOKENS:
        value = getattr(theme_module, token)
        assert isinstance(value, tuple), f"{token} is not a tuple"
        assert len(value) == 3, f"{token} does not have 3 components"
        for component in value:
            assert isinstance(component, int), f"{token} component is not int"
            assert 0 <= component <= 255, f"{token} component {component!r} out of 0-255"


def test_themes_contains_required_keys():
    assert "green" in THEMES
    assert "neutral" in THEMES


def test_theme_registry_set_theme_changes_active():
    registry = ThemeRegistry()
    assert registry.active.name == "green"
    registry.set_theme("neutral")
    assert registry.active.name == "neutral"
