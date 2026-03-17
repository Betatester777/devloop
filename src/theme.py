# Implements: REQ-7 AC-7.1 — brand palette tokens, Theme dataclass, ThemeRegistry
# See: ARC §src/theme.py

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Palette constants — values from PRD colour reference (REQ-6)
# ---------------------------------------------------------------------------
G900: tuple[int, int, int] = (0, 86, 35)
G800: tuple[int, int, int] = (0, 108, 44)
G700: tuple[int, int, int] = (0, 129, 52)
G600: tuple[int, int, int] = (0, 151, 61)
G500: tuple[int, int, int] = (0, 172, 70)
G400: tuple[int, int, int] = (43, 189, 101)
G300: tuple[int, int, int] = (87, 205, 132)
G200: tuple[int, int, int] = (130, 219, 163)
G100: tuple[int, int, int] = (173, 233, 195)
G20: tuple[int, int, int] = (204, 238, 218)
G15: tuple[int, int, int] = (217, 243, 227)

N100: tuple[int, int, int] = (251, 251, 251)
N100Bold: tuple[int, int, int] = (237, 237, 237)
N100Bolder: tuple[int, int, int] = (214, 214, 214)
N200: tuple[int, int, int] = (243, 245, 243)
N200Bold: tuple[int, int, int] = (226, 228, 226)
N200Bolder: tuple[int, int, int] = (204, 206, 204)
N300: tuple[int, int, int] = (237, 239, 238)
N400: tuple[int, int, int] = (220, 223, 220)
N500: tuple[int, int, int] = (178, 180, 181)
N600: tuple[int, int, int] = (145, 147, 148)
N700: tuple[int, int, int] = (112, 115, 117)


@dataclass
class Theme:
    """Maps semantic UI roles to palette colour values."""

    name: str
    background: tuple[int, int, int]
    surface: tuple[int, int, int]
    primary: tuple[int, int, int]
    on_primary: tuple[int, int, int]
    text: tuple[int, int, int]
    text_muted: tuple[int, int, int]
    focus_ring: tuple[int, int, int]
    card_back: tuple[int, int, int]
    card_front_border: tuple[int, int, int]


THEMES: dict[str, Theme] = {
    "green": Theme(
        name="green",
        background=G900,
        surface=G800,
        primary=G500,
        on_primary=N100,
        text=N100,
        text_muted=G200,
        focus_ring=G400,
        card_back=G700,
        card_front_border=G400,
    ),
    "neutral": Theme(
        name="neutral",
        background=N300,
        surface=N200,
        primary=G500,
        on_primary=N100,
        text=N700,
        text_muted=N600,
        focus_ring=G400,
        card_back=N400,
        card_front_border=N500,
    ),
}


class ThemeRegistry:
    """Holds the currently active theme and allows switching by name."""

    def __init__(self) -> None:
        self.active: Theme = THEMES["green"]

    def set_theme(self, name: str) -> None:
        if name not in THEMES:
            raise KeyError(f"Unknown theme: {name!r}")
        self.active = THEMES[name]
