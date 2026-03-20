# Implements: REQ-1 AC-1.1 — Brand color palette and light/dark theme definitions
# See: ARC SS 12 (theme), ADR-6 (Color Theme Implementation)
from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
Color = tuple[int, int, int]

# ---------------------------------------------------------------------------
# Brand green palette (exact hex values from PRD)
# ---------------------------------------------------------------------------
G900: Color = (0x00, 0x56, 0x23)   # #005623
G800: Color = (0x00, 0x6C, 0x2C)   # #006c2c
G700: Color = (0x00, 0x81, 0x34)   # #008134
G600: Color = (0x00, 0x97, 0x3D)   # #00973d
G500: Color = (0x00, 0xAC, 0x46)   # #00ac46
G400: Color = (0x2B, 0xBD, 0x65)   # #2bbd65
G300: Color = (0x57, 0xCD, 0x84)   # #57cd84
G200: Color = (0x82, 0xDB, 0xA3)   # #82dba3
G100: Color = (0xAD, 0xE9, 0xC3)   # #ade9c3
G20: Color = (0xCC, 0xEE, 0xDA)    # #cceeda
G15: Color = (0xD9, 0xF3, 0xE3)    # #d9f3e3

# ---------------------------------------------------------------------------
# Neutral palette (exact hex values from PRD)
# ---------------------------------------------------------------------------
N100: Color = (0xFB, 0xFB, 0xFB)       # #fbfbfb
N100_BOLD: Color = (0xED, 0xED, 0xED)   # #ededed
N100_BOLDER: Color = (0xD6, 0xD6, 0xD6) # #d6d6d6
N200: Color = (0xF3, 0xF5, 0xF3)        # #f3f5f3
N200_BOLD: Color = (0xE2, 0xE4, 0xE2)   # #e2e4e2
N200_BOLDER: Color = (0xCC, 0xCE, 0xCC) # #cccecc
N300: Color = (0xED, 0xEF, 0xEE)        # #edefee
N400: Color = (0xDC, 0xDF, 0xDC)        # #dcdfdc
N500: Color = (0xB2, 0xB4, 0xB5)        # #b2b4b5
N600: Color = (0x91, 0x93, 0x94)        # #919394
N700: Color = (0x70, 0x73, 0x75)        # #707375

WHITE: Color = (255, 255, 255)
BLACK: Color = (0, 0, 0)


# ---------------------------------------------------------------------------
# Theme dataclass
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Theme:
    """Complete visual theme used by all screens."""

    name: str
    background: Color
    card_back: Color
    card_face: Color
    text_primary: Color
    text_secondary: Color
    accent: Color
    focus_indicator: Color
    button_bg: Color
    button_text: Color
    timer_bar: Color
    success: Color
    failure: Color


# ---------------------------------------------------------------------------
# Pre-defined themes
# ---------------------------------------------------------------------------
LIGHT_THEME = Theme(
    name="light",
    background=N100,
    card_back=G700,
    card_face=WHITE,
    text_primary=N700,
    text_secondary=N500,
    accent=G500,
    focus_indicator=G500,
    button_bg=G500,
    button_text=WHITE,
    timer_bar=G500,
    success=G500,
    failure=(0xD3, 0x2F, 0x2F),  # a readable red for failure feedback
)

DARK_THEME = Theme(
    name="dark",
    background=N700,
    card_back=G900,
    card_face=N600,
    text_primary=N100,
    text_secondary=N400,
    accent=G300,
    focus_indicator=G300,
    button_bg=G300,
    button_text=N700,
    timer_bar=G300,
    success=G300,
    failure=(0xEF, 0x53, 0x50),  # brighter red on dark background
)

_THEMES: dict[str, Theme] = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
}


def get_theme(name: str) -> Theme:
    """Return a theme by name. Raises ``ValueError`` for unknown names."""
    try:
        return _THEMES[name]
    except KeyError:
        valid = ", ".join(sorted(_THEMES))
        raise ValueError(
            f"Unknown theme '{name}'. Valid themes: {valid}"
        ) from None
