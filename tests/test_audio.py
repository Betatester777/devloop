# Verifies: AC-6.2 — AudioManager plays sounds on events
# Verifies: AC-6.3 — Sound files located under src/assets/sounds/

from __future__ import annotations

from src.audio import AudioManager, SoundEvent, _SOUNDS_DIR


class TestSoundEvent:
    def test_five_events_defined(self):
        assert len(SoundEvent) == 5

    def test_event_values_match_filenames(self):
        expected = {"flip", "match", "not_match", "win", "loose"}
        assert {e.value for e in SoundEvent} == expected


class TestSoundsDirectory:
    """AC-6.3: all sound files under src/assets/sounds/."""

    def test_sounds_dir_exists(self):
        assert _SOUNDS_DIR.is_dir()

    def test_all_five_mp3s_present(self):
        for event in SoundEvent:
            path = _SOUNDS_DIR / f"{event.value}.mp3"
            assert path.is_file(), f"Missing: {path}"


class TestAudioManagerMute:
    def test_muted_by_default_is_false(self):
        mgr = AudioManager()
        assert mgr.muted is False

    def test_set_muted(self):
        mgr = AudioManager()
        mgr.set_muted(True)
        assert mgr.muted is True

    def test_play_does_not_crash_when_muted(self):
        mgr = AudioManager()
        mgr.set_muted(True)
        mgr.play(SoundEvent.FLIP)  # Should not raise


class TestAudioManagerPlay:
    def test_play_does_not_crash(self):
        mgr = AudioManager()
        mgr.play(SoundEvent.FLIP)  # Should not raise

    def test_play_when_unavailable(self):
        mgr = AudioManager()
        mgr._available = False
        mgr.play(SoundEvent.MATCH)  # Should not raise

    def test_play_missing_sound(self):
        mgr = AudioManager()
        mgr._sounds = {}  # Empty - simulate missing files
        mgr.play(SoundEvent.WIN)  # Should not raise
