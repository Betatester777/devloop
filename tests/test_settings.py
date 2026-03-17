# Verifies: AC-6.5 — Settings persistence (save/load round trip, defaults)

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.settings import Settings


@pytest.fixture()
def settings_path(tmp_path: Path) -> Path:
    return tmp_path / "settings.json"


class TestSettingsDefaults:
    def test_defaults_on_missing_file(self, settings_path: Path):
        s = Settings(settings_path=settings_path)
        assert s.theme == "green"
        assert s.sound_enabled is True
        assert s.music_enabled is True
        assert s.animation_mode == "full"

    def test_defaults_on_corrupt_file(self, settings_path: Path):
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text("{bad json", encoding="utf-8")
        s = Settings(settings_path=settings_path)
        assert s.theme == "green"


class TestSettingsPersistence:
    """AC-6.5: mute state (and all settings) preserved across restarts."""

    def test_save_creates_file(self, settings_path: Path):
        s = Settings(settings_path=settings_path)
        s.save()
        assert settings_path.is_file()

    def test_round_trip(self, settings_path: Path):
        s = Settings(settings_path=settings_path)
        s.theme = "neutral"
        s.sound_enabled = False
        s.music_enabled = False
        s.animation_mode = "reduced"
        s.save()

        s2 = Settings(settings_path=settings_path)
        assert s2.theme == "neutral"
        assert s2.sound_enabled is False
        assert s2.music_enabled is False
        assert s2.animation_mode == "reduced"

    def test_overwrite(self, settings_path: Path):
        s = Settings(settings_path=settings_path)
        s.sound_enabled = False
        s.save()
        s.sound_enabled = True
        s.save()
        s2 = Settings(settings_path=settings_path)
        assert s2.sound_enabled is True

    def test_file_is_valid_json(self, settings_path: Path):
        s = Settings(settings_path=settings_path)
        s.save()
        data = json.loads(settings_path.read_text("utf-8"))
        assert "theme" in data
        assert "sound_enabled" in data
