import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace


APP_PAYLOAD = Path(os.environ["APP_PAYLOAD"])
CORE_PATH = APP_PAYLOAD / "spotify_recovered_core.py"


def load_core_module():
    spec = importlib.util.spec_from_file_location("spotify_recovered_core_under_test", CORE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_host():
    return SimpleNamespace(
        spotify_pirate_next_loot=0.0,
        spotify_pirate_next_toploot=0.0,
        spotify_pirate_state="FARM",
        spotify_pirate_phase_started=0.0,
        spotify_pirate_last_toploot=0.0,
        spotify_pirate_last_loot=0.0,
        spotify_pirate_top_substate="MOVE_TOP",
        spotify_pirate_loot_substate="TO_START",
        spotify_pirate_loot_dir=1,
    )


def run_schedule(one_hit):
    mod = load_core_module()
    host = make_host()
    core = mod.SpotifyRecoveredCore(host)
    cfg = {
        "auto_loot": False,
        "spotify_loot_enabled": False,
        "map_profile": {},
    }
    result = core._spotify_pirate_schedule_step(
        cfg,
        map_pos=(100.0, 170.0),
        now=1.0,
        one_hit=one_hit,
    )
    return mod, host, core, cfg, result


def test_pirate_normal_schedule_ignores_generic_auto_loot_toggle():
    _, host, _, _, result = run_schedule(one_hit=False)
    assert host.spotify_pirate_next_loot > 0.0
    assert host.spotify_pirate_next_toploot > 0.0
    assert result is False


def test_pirate_one_hit_schedule_ignores_generic_auto_loot_toggle():
    _, host, _, _, result = run_schedule(one_hit=True)
    assert host.spotify_pirate_next_loot > 0.0
    assert host.spotify_pirate_next_toploot > 0.0
    assert result is False


def test_generic_loot_remains_gated_when_auto_loot_is_off():
    mod, host, core, cfg, _ = run_schedule(one_hit=False)
    host.spotify_last_loot_time = 0.0
    host.spotify_next_loot_delay = 0.0
    cfg["loot_key"] = "Z"
    cfg["loot_time"] = 90
    assert core._spotify_generic_loot_due(cfg, now=9999.0) is False


def test_dynamic_combo_and_simple_callers_are_not_modified_by_overlay():
    text = CORE_PATH.read_text(encoding="utf-8")
    # Dynamic Combo remains definition-only for this patch.
    assert text.count("_spotify_dynamic_combo_reconstructed(") == 1
    # The shared SIMPLE/Pirate combo primitive remains present and unchanged in routing intent.
    assert "def _spotify_hold_combo_action(" in text
    assert "def _spotify_primary_skill_step(" in text
