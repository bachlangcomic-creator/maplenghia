from types import SimpleNamespace

import pytest
from spotify_recovered_core import SpotifyRecoveredCore


class FakeHost(SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.events = []
        self.current_move_key = None
        self.spotify_input_role = "IDLE"
        self.spotify_input_last_role = ""
        self.spotify_input_last_key = ""

    def _focus_game(self, cfg):
        return True

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

    def _release_all_owned_inputs(self):
        self.release_move()
        self.events.append(("release_all",))

    def _log(self, text):
        self.events.append(("log", text))


def combo_cfg():
    return {"pause_on_focus_loss": False}


def test_hold_combo_accepts_flash_key_and_orders_flash_before_skill(monkeypatch):
    host = FakeHost()
    core = SpotifyRecoveredCore(host)
    sleeps = []
    uniform_values = iter([0.015, 0.125])
    monotonic_values = iter([10.0, 10.0, 10.4])
    monkeypatch.setattr("spotify_recovered_core.random.uniform", lambda a, b: next(uniform_values))
    monkeypatch.setattr("spotify_recovered_core.time.sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: next(monotonic_values))

    ok = core._spotify_hold_combo_action(combo_cfg(), "RIGHT", "T", "A", 0.2)

    assert ok is True
    presses = [e for e in host.events if e[0] == "press"]
    assert [e[1] for e in presses[:2]] == ["T", "A"]
    assert sleeps == [0.015, 0.125]


def test_hold_combo_flash_none_falls_back_to_skill_only(monkeypatch):
    host = FakeHost()
    core = SpotifyRecoveredCore(host)
    uniform_values = iter([0.125])
    monotonic_values = iter([20.0, 20.0, 20.4])
    monkeypatch.setattr("spotify_recovered_core.random.uniform", lambda a, b: next(uniform_values))
    monkeypatch.setattr("spotify_recovered_core.time.sleep", lambda _s: None)
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: next(monotonic_values))

    ok = core._spotify_hold_combo_action(combo_cfg(), "LEFT", None, "A", 0.2)

    assert ok is True
    presses = [e[1] for e in host.events if e[0] == "press"]
    assert presses == ["A"]


def test_hold_combo_missing_skill_fails_closed(monkeypatch):
    host = FakeHost()
    core = SpotifyRecoveredCore(host)
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: 30.0)

    ok = core._spotify_hold_combo_action(combo_cfg(), "LEFT", "T", None, 0.2)

    assert ok is False
    assert not [e for e in host.events if e[0] == "press"]


def test_hold_combo_input_exception_releases_owned_inputs(monkeypatch):
    host = FakeHost()
    core = SpotifyRecoveredCore(host)
    monotonic_values = iter([40.0, 40.0])
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: next(monotonic_values))
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_tap_combo", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("input boom")))

    with pytest.raises(RuntimeError, match="input boom"):
        core._spotify_hold_combo_action(combo_cfg(), "RIGHT", "T", "A", 0.2)

    assert ("release_all",) in host.events
    assert host.current_move_key is None
