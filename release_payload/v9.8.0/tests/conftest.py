from types import SimpleNamespace
import pytest


class FakeHost(SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.events = []
        self.current_move_key = None
        self.spotify_primary_held_key = None
        self.spotify_r54_safe_state = "MOVE_SAFE"
        self.spotify_r54_safe_arrived_at = 0.0
        self.spotify_r54_safe_verify_count = 0

    def __getattr__(self, name):
        if name.startswith("spotify_") or name.startswith("last_"):
            return 0
        raise AttributeError(name)

    def set_move(self, key):
        self.current_move_key = key
        self.events.append(("move", key))
        return True

    def release_move(self):
        if self.current_move_key:
            self.events.append(("move_up", self.current_move_key))
        self.current_move_key = None

    def _press_input_key(self, key, hold_ms=None):
        self.events.append(("press", key, hold_ms))
        return True

    def _input_key_down(self, key):
        self.events.append(("down", key))
        return True

    def _input_key_up(self, key):
        self.events.append(("up", key))
        return True

    def _log(self, text):
        self.events.append(("log", text))


@pytest.fixture
def fake_host():
    return FakeHost()
