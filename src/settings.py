# Implements: REQ-6 AC-6.5 — Persistent user preferences
# See: ARC §src/settings.py

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

_SETTINGS_DIR = Path.home() / ".delicious_memory"
_SETTINGS_FILE = _SETTINGS_DIR / "settings.json"

_DEFAULTS = {
    "theme": "green",
    "sound_enabled": True,
    "music_enabled": True,
    "animation_mode": "full",
}


class Settings:
    """Read and write user preferences to ``~/.delicious_memory/settings.json``."""

    def __init__(self, *, settings_path: Path | None = None) -> None:
        self._path = settings_path or _SETTINGS_FILE
        self.theme: str = _DEFAULTS["theme"]
        self.sound_enabled: bool = _DEFAULTS["sound_enabled"]
        self.music_enabled: bool = _DEFAULTS["music_enabled"]
        self.animation_mode: str = _DEFAULTS["animation_mode"]
        self.load()

    def load(self) -> None:
        """Load settings from disk, falling back to defaults."""
        if not self._path.is_file():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self.theme = str(data.get("theme", _DEFAULTS["theme"]))
            self.sound_enabled = bool(data.get("sound_enabled", _DEFAULTS["sound_enabled"]))
            self.music_enabled = bool(data.get("music_enabled", _DEFAULTS["music_enabled"]))
            self.animation_mode = str(data.get("animation_mode", _DEFAULTS["animation_mode"]))
        except (json.JSONDecodeError, TypeError, KeyError):
            pass  # Corrupt file — keep defaults

    def save(self) -> None:
        """Persist current settings atomically."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(
            {
                "theme": self.theme,
                "sound_enabled": self.sound_enabled,
                "music_enabled": self.music_enabled,
                "animation_mode": self.animation_mode,
            },
            indent=2,
        )
        fd, tmp = tempfile.mkstemp(dir=str(self._path.parent), suffix=".tmp")
        try:
            os.write(fd, data.encode("utf-8"))
            os.close(fd)
            os.replace(tmp, str(self._path))
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
