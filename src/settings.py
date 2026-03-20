# Implements: REQ-1 AC-1.1 — User preferences with JSON persistence
# See: ARC SS 11 (settings), ADR-5 (Settings Persistence), ADR-9 (Cross-Platform File Paths)
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


def _default_config_dir() -> Path:
    """Return the platform-appropriate config directory."""
    if os.name == "nt":
        base = os.environ.get("APPDATA", str(Path.home()))
        return Path(base) / "DeliciousMemory"
    return Path.home() / ".delicious_memory"


@dataclass
class Settings:
    """User preferences — all fields have sensible defaults."""

    sound_muted: bool = False
    theme_name: str = "light"
    category: str = "dishes"
    difficulty: str = "normal"
    timed_mode: bool = False
    reduced_animation: bool = False


class SettingsManager:
    """Loads and saves :class:`Settings` as JSON."""

    def __init__(self, config_path: Path | None = None) -> None:
        if config_path is None:
            config_path = _default_config_dir() / "settings.json"
        self._path = config_path

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> Settings:
        """Read settings from disk; return defaults on any failure."""
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return Settings()
            # Only accept known keys — ignore extras, fill missing with defaults
            defaults = Settings()
            return Settings(
                sound_muted=data.get("sound_muted", defaults.sound_muted),
                theme_name=data.get("theme_name", defaults.theme_name),
                category=data.get("category", defaults.category),
                difficulty=data.get("difficulty", defaults.difficulty),
                timed_mode=data.get("timed_mode", defaults.timed_mode),
                reduced_animation=data.get("reduced_animation", defaults.reduced_animation),
            )
        except Exception:
            return Settings()

    def save(self, settings: Settings) -> None:
        """Persist settings to disk. Creates parent directories if needed."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(asdict(settings), indent=2) + "\n",
            encoding="utf-8",
        )
