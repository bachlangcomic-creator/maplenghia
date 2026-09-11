import ast
import json
import os
from pathlib import Path

from spotify_behavior_engine import SpotifyBehaviorEngine
from spotify_recovered_core import SpotifyRecoveredCore


def app_dir():
    return Path(os.environ.get("APP_PAYLOAD", "portable/app_payload"))


def function_source(path, name):
    text = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_dispatch_routes_each_mode_to_one_family(fake_host, monkeypatch):
    engine = SpotifyBehaviorEngine(fake_host)
    called = []
    monkeypatch.setattr(SpotifyBehaviorEngine, "_focus_guard", lambda *a, **k: True)
    monkeypatch.setattr(SpotifyBehaviorEngine, "_housekeeping", lambda *a, **k: None)
    monkeypatch.setattr(SpotifyBehaviorEngine, "_aux_allowed", lambda *a, **k: False)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_recovery_layer_step", lambda *a, **k: False)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_left_right_step", lambda *a, **k: called.append("SIMPLE") or True)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_bunny_step", lambda *a, **k: called.append("BUNNY") or True)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_stand_still_step", lambda *a, **k: called.append("STAND") or True)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_pirate_step", lambda self, cfg, pos, now, one_hit=False: called.append("PIRATE1" if one_hit else "PIRATE") or True)

    for kind, expected in [
        ("LEFT_RIGHT", "SIMPLE"),
        ("BUNNY", "BUNNY"),
        ("STAND_STILL", "STAND"),
        ("PIRATE2", "PIRATE"),
        ("PIRATE2_1HIT", "PIRATE1"),
    ]:
        called.clear()
        engine.last_profile_kind = kind
        assert engine.movement_step({"kind": kind, "pause_on_focus_loss": False}, (100, 169), 1.0)
        assert called == [expected]


def test_focus_worker_keeps_window_lookup_out_of_combat():
    src = function_source(app_dir() / "spotify_behavior_engine.py", "_spotify_focus_enforcer_worker")
    assert "_spotify_focus_refresh" in src
    assert "_find_game_window" not in src


def test_c2_fast_worker_uses_cached_hwnd_not_window_lookup():
    src = function_source(app_dir() / "maple_nghia_pro.py", "_c2_fast_farm_worker")
    assert "_spotify_cached_game_hwnd" in src
    assert "_find_game_window" not in src


def test_c2_recovered_ranges_remain_in_c2_combo():
    src = function_source(app_dir() / "spotify_recovered_core.py", "_spotify_c2_tp_skill_hold_combo")
    catalog = (app_dir() / "spotify_recovered_core.py").read_text(encoding="utf-8")
    for token in ("SPOTIFY_R54_COMBO_SPAM_ACTION_MS", "SPOTIFY_R54_COMBO_SPAM_WAIT_S"):
        assert token in src
    assert "(20, 50)" in catalog
    assert "(0.05, 0.15)" in catalog
    primary = function_source(app_dir() / "spotify_recovered_core.py", "_spotify_primary_skill_step")
    assert "SPOTIFY_SIMPLE_HOLD_COMBO_MS" in primary
    assert "(200, 500)" in catalog


def test_simple_profiles_match_recovered_coordinates():
    maps = json.loads((app_dir() / "maps.json").read_text(encoding="utf-8"))
    expected = {
        "C1": (85, 169, 135, 169, 118, 160),
        "C2": (32, 169, 196, 169, 67, 161),
        "B1": (72, 168, 137, 168, 83, 153),
        "B3": (72, 168, 155, 168, 154, 160),
    }
    for name, (lx, ly, rx, ry, sx, sy) in expected.items():
        p = maps[name]
        assert p["FARM_TYPE"] == "SIMPLE"
        assert (p["LEFT_X"], p["LEFT_Y"]) == (lx, ly)
        assert (p["RIGHT_X"], p["RIGHT_Y"]) == (rx, ry)
        assert (p["SAFE_PLACE_X"], p["SAFE_PLACE_Y"]) == (sx, sy)
        assert p["CHAR_MATCH_THRESHOLD"] == 0.6


def test_b3_fixed_y_is_default_and_adaptive_y_is_explicit_extension():
    host = (app_dir() / "maple_nghia_pro.py").read_text(encoding="utf-8")
    core = function_source(app_dir() / "spotify_recovered_core.py", "_spotify_left_right_step")
    assert "b3_adaptive_y_enabled" in host
    assert "b3_adaptive_y_enabled" in core
    assert "Nghĩa extension" in host or "Nghia extension" in host
    assert "b3_adaptive_y_enabled = tk.BooleanVar(value=False)" in host


def test_stop_releases_move_skill_and_invalidates_generation(fake_host, monkeypatch):
    engine = SpotifyBehaviorEngine(fake_host)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_reset_auxiliary_timers", lambda *a, **k: None)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_reset_recovery_layer", lambda *a, **k: None)
    engine.start({"kind": "BUNNY", "spotify_force_focus_parity": False})
    g = engine.generation
    fake_host.current_move_key = "RIGHT"
    fake_host.spotify_primary_held_key = "A"
    engine.stop()
    assert engine.generation == g + 1
    assert engine.running is False
    assert fake_host.current_move_key is None
    assert fake_host.spotify_primary_held_key is None
    assert ("up", "A") in fake_host.events
