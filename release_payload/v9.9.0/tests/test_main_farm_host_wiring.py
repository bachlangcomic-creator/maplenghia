import ast
import os
from pathlib import Path

APP = Path(os.environ["APP_PAYLOAD"])


def source(name):
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_bot_loop_calls_orchestrator_once():
    assert source("bot_loop").count("spotify_main_farm_orchestrator.tick(") == 1


def test_all_seven_host_stages_exist():
    for name in (
        "_spotify_mainfarm_state_stage",
        "_spotify_mainfarm_sell_safe_stage",
        "_spotify_mainfarm_pet_stage",
        "_spotify_mainfarm_recovery_stage",
        "_spotify_mainfarm_buff1_stage",
        "_spotify_mainfarm_buff2_stage",
        "_spotify_mainfarm_dispatch_stage",
    ):
        assert source(name).startswith("def ")


def test_stages_do_not_duplicate_sell_timer_or_completion():
    joined = "\n".join(
        source(n)
        for n in (
            "_spotify_mainfarm_state_stage",
            "_spotify_mainfarm_sell_safe_stage",
            "_spotify_mainfarm_pet_stage",
            "_spotify_mainfarm_recovery_stage",
            "_spotify_mainfarm_buff1_stage",
            "_spotify_mainfarm_buff2_stage",
            "_spotify_mainfarm_dispatch_stage",
        )
    )
    for forbidden in ("random.uniform", "sell_interval_minutes", "notify_sell_completed"):
        assert forbidden not in joined
    assert "spotify_sell_timer_event" in source("_spotify_mainfarm_sell_safe_stage")


def test_no_speculative_mainfarm_thread_and_c2_worker_stays_isolated():
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    assert "Nghia-Spotify-MainFarm" not in text
    c2 = source("_c2_fast_farm_worker").lower()
    for forbidden in ("watchdog", "all_cure", "market", "miumiu", "run_sell_thread"):
        assert forbidden not in c2


def test_dispatch_stage_preserves_c2_owner_and_non_c2_movement_owner():
    src = source("_spotify_mainfarm_dispatch_stage")
    assert "c2_fast_owned" in src
    assert "_dispatch_movement" in src
    assert "_spotify_auxiliary_step" in src


def test_pet_and_recovery_delegate_to_existing_subsystems():
    assert "behavior_engine.pet_step" in source("_spotify_mainfarm_pet_stage")
    assert "_spotify_recovery_layer_step" in source("_spotify_mainfarm_recovery_stage")
