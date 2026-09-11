import ast
import os
from pathlib import Path

APP = Path(os.environ.get("APP_PAYLOAD", Path(__file__).resolve().parents[3]))


def fn(path, name):
    text = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_c2_timing_and_cached_hwnd_remain_protected():
    core = (APP / "spotify_recovered_core.py").read_text(encoding="utf-8")
    combo = fn(APP / "spotify_recovered_core.py", "_spotify_c2_tp_skill_hold_combo")
    primary = fn(APP / "spotify_recovered_core.py", "_spotify_primary_skill_step")
    fast = fn(APP / "maple_nghia_pro.py", "_c2_fast_farm_worker")
    assert "SPOTIFY_R54_COMBO_SPAM_ACTION_MS = (20, 50)" in core
    assert "SPOTIFY_R54_COMBO_SPAM_WAIT_S = (0.05, 0.15)" in core
    assert "SPOTIFY_SIMPLE_HOLD_COMBO_MS = (200, 500)" in core
    assert "SPOTIFY_R54_COMBO_SPAM_ACTION_MS" in combo
    assert "SPOTIFY_R54_COMBO_SPAM_WAIT_S" in combo
    assert "SPOTIFY_SIMPLE_HOLD_COMBO_MS" in primary
    assert "_spotify_cached_game_hwnd" in fast
    assert "_find_game_window" not in fast


def test_dynamic_combo_remains_unwired():
    text = "\n".join(
        (APP / n).read_text(encoding="utf-8")
        for n in (
            "maple_nghia_pro.py",
            "spotify_behavior_engine.py",
            "spotify_recovered_core.py",
        )
    )
    assert text.count("_spotify_dynamic_combo_reconstructed(") == 1


def _v97_module_text(name):
    candidate = APP / name
    if candidate.exists():
        return candidate.read_text(encoding="utf-8")
    fallback = Path(__file__).resolve().parents[1] / name
    return fallback.read_text(encoding="utf-8")


def test_v97_does_not_invent_active_session_monitor():
    text = "\n".join(
        [
            (APP / "maple_nghia_pro.py").read_text(encoding="utf-8"),
            (APP / "spotify_behavior_engine.py").read_text(encoding="utf-8"),
            (APP / "spotify_recovered_core.py").read_text(encoding="utf-8"),
            _v97_module_text("spotify_watchdog.py"),
        ]
    )
    assert "def session_monitor_worker" not in text
    assert "def _session_monitor_worker" not in text


def test_dynamic_combo_has_no_new_caller():
    text = "\n".join(
        [
            (APP / "maple_nghia_pro.py").read_text(encoding="utf-8"),
            (APP / "spotify_behavior_engine.py").read_text(encoding="utf-8"),
            (APP / "spotify_recovered_core.py").read_text(encoding="utf-8"),
            _v97_module_text("spotify_watchdog.py"),
        ]
    )
    assert text.count("_spotify_dynamic_combo_reconstructed(") == 1
