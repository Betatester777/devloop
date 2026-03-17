# Verifies: AC-7.1 AC-7.3 AC-7.4 — SceneManager switch, delegation, isolation
# Requirement: REQ-7 (Responsive desktop UI)

from unittest.mock import MagicMock

import pygame
import pytest

from src.scene_manager import SceneManager
from src.scenes.base import Scene


@pytest.fixture(autouse=True)
def _pygame_init():
    pygame.init()
    yield
    pygame.quit()


def _mock_scene() -> MagicMock:
    return MagicMock(spec=Scene)


class TestSceneManagerSwitch:
    def test_switch_updates_current(self):
        scene_a = _mock_scene()
        scene_b = _mock_scene()
        sm = SceneManager(scene_a)
        assert sm.current is scene_a
        sm.switch(scene_b)
        assert sm.current is scene_b

    def test_switch_does_not_call_old_scene(self):
        scene_a = _mock_scene()
        scene_b = _mock_scene()
        sm = SceneManager(scene_a)
        sm.switch(scene_b)
        scene_a.handle_event.assert_not_called()
        scene_a.update.assert_not_called()
        scene_a.draw.assert_not_called()


class TestSceneManagerDelegation:
    def test_handle_event_delegates_once(self):
        scene = _mock_scene()
        sm = SceneManager(scene)
        event = pygame.event.Event(pygame.USEREVENT)
        sm.handle_event(event)
        scene.handle_event.assert_called_once_with(event)

    def test_update_delegates_once(self):
        scene = _mock_scene()
        sm = SceneManager(scene)
        sm.update(0.016)
        scene.update.assert_called_once_with(0.016)

    def test_draw_delegates_once(self):
        scene = _mock_scene()
        sm = SceneManager(scene)
        surface = MagicMock(spec=pygame.Surface)
        sm.draw(surface)
        scene.draw.assert_called_once_with(surface)
