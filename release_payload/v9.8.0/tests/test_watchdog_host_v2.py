import ast
import os
from pathlib import Path

APP = Path(os.environ.get("APP_PAYLOAD", "/mnt/data/v97_final_patchcheck"))


def app_source(name):
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(f"missing {name}")


def test_scan_bridge_uses_v98_exact_asset_detector_helpers():
    src = app_source("_spotify_watchdog_scan_frame")
    for required in ("detect_captcha_exact", "score_full_bag_variant", "score_dead", "score_disconnect"):
        assert required in src


def test_captcha_emit_is_pause_alert_only():
    src = app_source("_spotify_watchdog_emit")
    assert "_spotify_watchdog_request_pause" in src
    assert "_handle_alert" in src
    for forbidden in ("gemini", "generativeai", "captcha_answer", "solve_captcha"):
        assert forbidden not in src.lower()


def test_dead_emit_routes_to_evidence_gated_revive_bridge():
    src = app_source("_spotify_watchdog_emit")
    assert "_spotify_watchdog_request_revive" in src
    revive = app_source("_spotify_watchdog_request_revive")
    assert "return False" in revive
    assert "spotify_dead_center" in revive
    assert "pydirectinput.moveTo" in revive
    assert "pydirectinput.mouseDown" in revive
    assert "pydirectinput.mouseUp" in revive


def test_full_bag_emit_sets_event_but_never_calls_seller():
    src = app_source("_spotify_watchdog_emit")
    assert "spotify_full_bag_event.set()" in src
    assert "run_sell_thread" not in src
