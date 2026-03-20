# Verifies: AC-1.1 — Settings defaults, round-trip persistence, corrupt-file fallback
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.settings import Settings, SettingsManager


@pytest.fixture()
def config_path(tmp_path: Path) -> Path:
    return tmp_path / "settings.json"


class TestSettingsDefaults:
    def test_default_values(self) -> None:
        s = Settings()
        assert s.sound_muted is False
        assert s.theme_name == "light"
        assert s.category == "dishes"
        assert s.difficulty == "normal"
        assert s.timed_mode is False
        assert s.reduced_animation is False


class TestSettingsManagerRoundTrip:
    def test_save_and_load(self, config_path: Path) -> None:
        mgr = SettingsManager(config_path)
        original = Settings(
            sound_muted=True,
            theme_name="dark",
            category="drinks",
            difficulty="hard",
            timed_mode=True,
            reduced_animation=True,
        )
        mgr.save(original)
        loaded = mgr.load()
        assert loaded == original

    def test_load_missing_file_returns_defaults(self, config_path: Path) -> None:
        mgr = SettingsManager(config_path)
        loaded = mgr.load()
        assert loaded == Settings()


class TestSettingsManagerCorruptFile:
    def test_corrupt_json_returns_defaults(self, config_path: Path) -> None:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("NOT VALID JSON!!!", encoding="utf-8")
        mgr = SettingsManager(config_path)
        loaded = mgr.load()
        assert loaded == Settings()

    def test_non_dict_json_returns_defaults(self, config_path: Path) -> None:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
        mgr = SettingsManager(config_path)
        loaded = mgr.load()
        assert loaded == Settings()

    def test_partial_data_fills_defaults(self, config_path: Path) -> None:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps({"sound_muted": True}), encoding="utf-8")
        mgr = SettingsManager(config_path)
        loaded = mgr.load()
        assert loaded.sound_muted is True
        assert loaded.theme_name == "light"  # default filled in
