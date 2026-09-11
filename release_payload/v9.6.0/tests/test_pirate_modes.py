import inspect

import spotify_recovered_core as c
from spotify_recovered_core import SpotifyRecoveredCore


def pirate_cfg():
    return {
        "left_key": "LEFT", "right_key": "RIGHT", "jump_key": "J", "tele_key": "T",
        "spotify_attack_key": "A", "loot_key": "L", "pause_on_focus_loss": False,
        "spotify_loot_enabled": True, "auto_loot": True,
        "map_profile": {
            "LEFT_X": 50, "LEFT_Y": 172, "RIGHT_X": 180, "RIGHT_Y": 172,
            "LOOT_BOT_RIGHT_X": 189, "LOOT_BOT_RIGHT_Y": 196,
            "LOOT_BOT_LEFT_X": 80, "LOOT_BOT_LEFT_Y": 196,
            "LOOT_BOT_1_X": 105, "LOOT_BOT_1_Y": 201,
            "LOOT_BOT_2_X": 170, "LOOT_BOT_2_Y": 201,
        },
    }


def test_normal_pirate_edge_runs_human_branch_after_reverse(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.map_move_direction = 1
    monkeypatch.setattr("spotify_recovered_core.random.random", lambda: 0.01)
    monkeypatch.setattr("spotify_recovered_core.random.randint", lambda a, b: a)
    sleeps = []
    monkeypatch.setattr("spotify_recovered_core.time.sleep", lambda s: sleeps.append(s))
    assert core._spotify_pirate_normal_farm_step(pirate_cfg(), (176, 172), 10.0)
    assert fake_host.map_move_direction == -1
    assert any(e[0] == "press" and e[1] == "J" for e in fake_host.events)
    assert c.SPOTIFY_PIRATE_FARM_TURN_SLEEP in sleeps


def test_normal_pirate_moving_combo_does_not_reuse_edge_jump(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.map_move_direction = 1
    fake_host.spotify_pirate_farm_next_attack = 0.0
    monkeypatch.setattr("spotify_recovered_core.random.random", lambda: 0.01)
    monkeypatch.setattr("spotify_recovered_core.time.sleep", lambda _s: None)
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: 10.0)
    assert core._spotify_pirate_normal_farm_step(pirate_cfg(), (100, 172), 10.0)
    assert not any(e[0] == "press" and e[1] == "J" for e in fake_host.events)
    assert any(e[0] == "down" and e[1] == "A" for e in fake_host.events)


def test_pirate_route_constants():
    assert c.SPOTIFY_PIRATE_TOP_LOOT_POS == (135.0, 177.0)
    assert c.SPOTIFY_PIRATE_TOP_RETURN_POS == (114.0, 172.0)
    assert c.SPOTIFY_PIRATE_TOP_CAST_HOLD_MS == (800, 1500)
    assert c.SPOTIFY_PIRATE_TOP_FLASH_HOLD_MS == (100, 150)
    assert c.SPOTIFY_PIRATE_TOP_SKILL_HOLD_MS == (1000, 1500)
    assert c.SPOTIFY_PIRATE_SWEEP_HOLD_SECONDS == 1.6
    assert c.SPOTIFY_PIRATE_1HIT_SWEEP_HOLD_SECONDS == 1.5


def test_one_hit_right_wait_then_one_press(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.map_move_direction = 1
    fake_host.spotify_pirate_onehit_state = "MOVE"
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_pirate_fall_recovery", lambda *a, **k: False)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_move_to_step", lambda *a, **k: True)
    monkeypatch.setattr("spotify_recovered_core.random.randint", lambda a, b: 300)
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: 10.1)
    assert core._spotify_pirate_1hit_farm_step(pirate_cfg(), (180, 172), 10.0)
    assert fake_host.spotify_pirate_onehit_state == "RIGHT_SETUP"
    assert core._spotify_pirate_1hit_farm_step(pirate_cfg(), (178, 183), 10.1)
    assert fake_host.spotify_pirate_onehit_state == "RIGHT_WAIT"
    wait = fake_host.spotify_pirate_onehit_wait_until
    fake_host.events.clear()
    assert core._spotify_pirate_1hit_farm_step(pirate_cfg(), (178, 183), wait + 0.01)
    presses = [e for e in fake_host.events if e[0] == "press" and e[1] == "A"]
    assert len(presses) == 1


def test_one_hit_left_wait_exact_1_5(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.map_move_direction = -1
    fake_host.spotify_pirate_onehit_state = "MOVE"
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_pirate_fall_recovery", lambda *a, **k: False)
    assert core._spotify_pirate_1hit_farm_step(pirate_cfg(), (50, 172), 20.0)
    assert fake_host.spotify_pirate_onehit_state == "LEFT_WAIT"
    assert fake_host.spotify_pirate_onehit_wait_until == 21.5


def test_one_hit_prohibits_continuous_attack_worker():
    src = inspect.getsource(SpotifyRecoveredCore._spotify_pirate_1hit_farm_step)
    assert "_spotify_hold_combo_action" not in src
    assert "_spotify_pirate_normal_farm_step" not in src


def test_normal_bottom_loot_completion_alternates_sweep_direction(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_pirate_state = "LOOTING_BOT_2"
    fake_host.spotify_pirate_loot_dir = 1
    fake_host.spotify_pirate_phase_started = 9.0
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_move_to_step", lambda *a, **k: True)
    monkeypatch.setattr("spotify_recovered_core.time.sleep", lambda _s: None)
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: 10.0)
    monkeypatch.setattr("spotify_recovered_core.random.uniform", lambda a, b: a)
    monkeypatch.setattr("spotify_recovered_core.random.randint", lambda a, b: a)

    assert core._spotify_pirate_schedule_step(pirate_cfg(), (180, 172), 10.0, one_hit=False)
    assert fake_host.spotify_pirate_state == "FARM"
    assert fake_host.spotify_pirate_loot_dir == -1


def test_one_hit_bottom_loot_completion_keeps_fixed_sweep_and_returns_right(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_pirate_state = "LOOTING_BOT_2"
    fake_host.spotify_pirate_loot_dir = 1
    fake_host.map_move_direction = -1
    fake_host.spotify_pirate_phase_started = 9.0
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_move_to_step", lambda *a, **k: True)
    monkeypatch.setattr("spotify_recovered_core.time.sleep", lambda _s: None)
    monkeypatch.setattr("spotify_recovered_core.time.monotonic", lambda: 10.0)
    monkeypatch.setattr("spotify_recovered_core.random.uniform", lambda a, b: a)
    monkeypatch.setattr("spotify_recovered_core.random.randint", lambda a, b: a)

    assert core._spotify_pirate_schedule_step(pirate_cfg(), (189, 196), 10.0, one_hit=True)
    assert fake_host.spotify_pirate_state == "FARM"
    assert fake_host.spotify_pirate_loot_dir == 1
    assert fake_host.map_move_direction == 1
    assert fake_host.spotify_pirate_onehit_state == "MOVE"
