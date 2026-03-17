# Implements: REQ-6 AC-6.2, AC-6.3 — Sound effects for game events
# See: ARC §src/audio.py

from __future__ import annotations

from enum import Enum
from pathlib import Path

_SOUNDS_DIR = Path(__file__).resolve().parent / "assets" / "sounds"


class SoundEvent(Enum):
    """Named sound events matching the five MP3 files (AC-6.3)."""

    FLIP = "flip"
    MATCH = "match"
    MISMATCH = "not_match"
    WIN = "win"
    LOSE = "loose"


class AudioManager:
    """Load and play sound effects; respect mute state (AC-6.2).

    Gracefully degrades when pygame.mixer is unavailable.
    """

    def __init__(self) -> None:
        self.muted: bool = False
        self._sounds: dict[SoundEvent, object] = {}
        self._available: bool = False
        self._load_sounds()

    def _load_sounds(self) -> None:
        try:
            import pygame.mixer

            if not pygame.mixer.get_init():
                pygame.mixer.init()
            for event in SoundEvent:
                path = _SOUNDS_DIR / f"{event.value}.mp3"
                if path.is_file():
                    self._sounds[event] = pygame.mixer.Sound(str(path))
            self._available = True
        except Exception:
            self._available = False

    def play(self, event: SoundEvent) -> None:
        """Play the sound for *event* unless muted or unavailable."""
        if self.muted or not self._available:
            return
        sound = self._sounds.get(event)
        if sound is not None:
            sound.play()  # type: ignore[union-attr]

    def set_muted(self, muted: bool) -> None:
        self.muted = muted
