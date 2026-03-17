# Implements: REQ-5 AC-5.1, AC-5.2, AC-5.3, AC-5.4 — Save/load game state
# See: ARC §src/save.py

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from src.game.state import GameState

_SAVE_DIR = Path.home() / ".delicious_memory"
_SAVE_FILE = _SAVE_DIR / "save.json"


class SaveError(Exception):
    """Human-readable error for save/load failures (AC-5.4)."""


class SaveManager:
    """Serialise/deserialise GameState to ``~/.delicious_memory/save.json``."""

    def __init__(self, *, save_path: Path | None = None) -> None:
        self._path = save_path or _SAVE_FILE

    def save(self, state: GameState) -> None:
        """Write *state* atomically to the save file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(state.to_dict(), indent=2)
        # Atomic write: write to temp then rename
        fd, tmp = tempfile.mkstemp(
            dir=str(self._path.parent), suffix=".tmp"
        )
        try:
            os.write(fd, data.encode("utf-8"))
            os.close(fd)
            os.replace(tmp, str(self._path))
        except Exception:
            os.close(fd) if not os.get_inheritable(fd) else None  # noqa: E701
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    def load(self) -> GameState:
        """Load and return the saved GameState.

        Raises ``SaveError`` if the file is absent, corrupted, or incompatible (AC-5.4).
        """
        if not self._path.is_file():
            raise SaveError("No save file found")
        try:
            text = self._path.read_text(encoding="utf-8")
            data = json.loads(text)
            return GameState.from_dict(data)
        except json.JSONDecodeError as exc:
            raise SaveError(f"Save file is corrupted: {exc}") from exc
        except (KeyError, ValueError, TypeError) as exc:
            raise SaveError(f"Save file is incompatible: {exc}") from exc

    def has_save(self) -> bool:
        """True when a save file exists on disk (AC-5.3)."""
        return self._path.is_file()

    def delete(self) -> None:
        """Remove the save file if it exists."""
        if self._path.is_file():
            self._path.unlink()
