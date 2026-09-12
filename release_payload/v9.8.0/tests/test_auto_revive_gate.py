import ast
import json
import os
from pathlib import Path

APP = Path(os.environ.get("APP_PAYLOAD", "/mnt/data/v98_task2_check"))
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence" / "revive_action.json"


def app_source(name):
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_revive_evidence_is_exactly_the_recovered_dynamic_target():
    e = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert e["asset"] == "DEAD_B64"
    assert e["detector_threshold"] == 0.8
    assert e["target"] == "matched_template_center"
    assert e["move_duration_s"] == 0.1
    assert e["mouse_down_s"] == 0.05


def test_dead_scan_caches_matched_center_at_recovered_threshold():
    src = app_source("_spotify_watchdog_scan_frame")
    assert "spotify_dead_center" in src
    assert "threshold=0.80" in src or "threshold=0.8" in src
    assert "path_is_exact=True" in src


def test_revive_releases_before_evidenced_click_sequence():
    src = app_source("_spotify_watchdog_request_revive")
    pause = src.index("_spotify_watchdog_request_pause")
    move = src.index("pydirectinput.moveTo")
    assert pause < move
    assert "spotify_dead_center" in src
    assert "duration=0.10" in src or "duration=0.1" in src
    assert "pydirectinput.mouseDown()" in src
    assert "time.sleep(0.05)" in src
    assert "pydirectinput.mouseUp()" in src
    assert "return True" in src


def test_revive_fails_closed_without_center_or_input_backend():
    src = app_source("_spotify_watchdog_request_revive")
    assert "if not center" in src
    assert "pydirectinput is None" in src
    assert "return False" in src
