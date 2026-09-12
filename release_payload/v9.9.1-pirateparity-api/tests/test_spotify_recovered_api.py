import os
import sys
from pathlib import Path

APP_PAYLOAD = Path(os.environ["APP_PAYLOAD"])
sys.path.insert(0, str(APP_PAYLOAD))

from spotify_recovered_api import SpotifyRecoveredAPI
from spotify_behavior_engine import SpotifyBehaviorEngine


class RecordingCore:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def record(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return name
        return record


def test_restores_recovered_public_function_inventory():
    api = SpotifyRecoveredAPI(RecordingCore())
    expected = {
        "hold_combo_action", "left_flash", "left_jump", "move_and_jump",
        "right_jump", "random_move", "right_flash", "flash_down",
        "jump_down", "perform_dynamic_combo", "run_bunny",
        "run_stand_still", "run_pirate2", "run_pirate2_1hit",
        "run_left_and_right",
    }
    assert expected.issubset(set(dir(api)))


def test_dispatches_all_active_farm_profiles_through_recovered_api():
    core = RecordingCore()
    api = SpotifyRecoveredAPI(core)
    cfg = {"current_map": "C2"}
    cases = {
        "LEFT_RIGHT": "_spotify_left_right_step",
        "STAND_STILL": "_spotify_stand_still_step",
        "BUNNY": "_spotify_bunny_step",
        "PIRATE2": "_spotify_pirate_step",
        "PIRATE2_1HIT": "_spotify_pirate_step",
    }
    for kind, expected in cases.items():
        core.calls.clear()
        api.dispatch(kind, cfg, (100.0, 170.0), 12.0)
        assert core.calls[-1][0] == expected
    assert core.calls[-1][2]["one_hit"] is True


def test_behavior_engine_routes_profiles_through_public_api():
    class Host:
        def _spotify_profile_kind(self, cfg):
            return cfg["kind"]

    class RecordingAPI:
        def __init__(self):
            self.calls = []

        def dispatch(self, *args):
            self.calls.append(args)
            return "api-result"

    engine = SpotifyBehaviorEngine(Host())
    api = RecordingAPI()
    engine.api = api
    result = engine._dispatch_movement({"kind": "BUNNY"}, (55.0, 169.0), 20.0)
    assert result is True
    assert api.calls == [("BUNNY", {"kind": "BUNNY"}, (55.0, 169.0), 20.0)]


def test_dynamic_combo_is_exposed_but_not_wired_into_farm_dispatch():
    core = RecordingCore()
    api = SpotifyRecoveredAPI(core)
    result = api.perform_dynamic_combo({"current_map": "C2"}, "FOCUS", "RIGHT", hold_ms=250)
    assert result == "_spotify_dynamic_combo_reconstructed"
    assert core.calls[-1][0] == "_spotify_dynamic_combo_reconstructed"

    behavior = (APP_PAYLOAD / "spotify_behavior_engine.py").read_text(encoding="utf-8")
    assert "perform_dynamic_combo" not in behavior
