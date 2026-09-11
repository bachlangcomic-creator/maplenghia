import inspect

from spotify_recovered_core import SpotifyRecoveredCore


def base_cfg():
    return {
        "left_key": "LEFT", "right_key": "RIGHT", "spotify_attack_key": "A",
        "tele_key": "T", "tele_enabled": True, "pause_on_focus_loss": False,
        "spotify_loot_enabled": True, "auto_loot": True,
    }


def test_bunny_b_trigger_is_x_only(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_bunny_state = "TO_B"
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: 10.0)
    assert core._spotify_bunny_step(base_cfg(), (147, 222), 10.0)
    assert fake_host.spotify_bunny_state == "SPAM_B"
    assert any(e[0] == "press" and e[1] == "LEFT" and e[2] == 50 for e in fake_host.events)


def test_bunny_spam_expires_to_c(fake_host):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_bunny_state = "SPAM_B"
    fake_host.spotify_bunny_spam_start = 10.0
    fake_host.spotify_bunny_next_attack = 999.0
    assert core._spotify_bunny_step(base_cfg(), (147, 169), 13.01)
    assert fake_host.spotify_bunny_state == "TO_C"


def test_bunny_dispatch_never_calls_simple(fake_host, monkeypatch):
    from spotify_behavior_engine import SpotifyBehaviorEngine
    engine = SpotifyBehaviorEngine(fake_host)
    engine.last_profile_kind = "BUNNY"
    monkeypatch.setattr(SpotifyBehaviorEngine, "_focus_guard", lambda *a, **k: True)
    monkeypatch.setattr(SpotifyBehaviorEngine, "_housekeeping", lambda *a, **k: None)
    monkeypatch.setattr(SpotifyBehaviorEngine, "_aux_allowed", lambda *a, **k: False)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_recovery_layer_step", lambda *a, **k: False)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_left_right_step", lambda *a, **k: (_ for _ in ()).throw(AssertionError("SIMPLE called")))
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_bunny_step", lambda *a, **k: True)
    assert engine.movement_step({"kind": "BUNNY", "pause_on_focus_loss": False}, (100, 169), 1.0)


def test_stand_direct_skill_inside_anchor(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_stand_anchor = (100.0, 169.0)
    fake_host.spotify_stand_next_floor_jump = 9999.0
    cfg = {**base_cfg(), "current_map": "C1", "map_profile": {"SPOTIFY_SOURCE_MAP": "C1"}}
    assert core._spotify_stand_still_step(cfg, (102, 173), 5.0)
    presses = [e for e in fake_host.events if e[0] == "press" and e[1] == "A"]
    assert len(presses) == 1


def test_stand_recovery_outside_tolerance(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_stand_anchor = (100.0, 169.0)
    fake_host.spotify_stand_next_floor_jump = 9999.0
    calls = []
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_move_to_step", lambda self, cfg, pos, x, y, now, **kw: calls.append((x, y, kw)) or False)
    cfg = {**base_cfg(), "current_map": "C1", "map_profile": {"SPOTIFY_SOURCE_MAP": "C1"}}
    assert core._spotify_stand_still_step(cfg, (104, 169), 5.0)
    assert calls[0][0:2] == (100.0, 169.0)


def test_stand_loot_clears_anchor_for_observed_reacquire(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_stand_anchor = (100.0, 169.0)
    fake_host.spotify_stand_last_floor_jump = 0.0
    fake_host.spotify_stand_next_floor_jump = 1.0
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_move_to_step", lambda *a, **k: True)
    monkeypatch.setattr("spotify_recovered_core.time.sleep", lambda _s: None)
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: 10.0)
    cfg = {**base_cfg(), "current_map": "C1", "map_profile": {"SPOTIFY_SOURCE_MAP": "C1"}}
    assert core._spotify_stand_c1_loot_step(cfg, (125, 160), 10.0)
    assert fake_host.spotify_stand_anchor is None


def test_stand_still_does_not_use_hold_combo():
    src = inspect.getsource(SpotifyRecoveredCore._spotify_stand_still_step)
    assert "_spotify_hold_combo_action" not in src
