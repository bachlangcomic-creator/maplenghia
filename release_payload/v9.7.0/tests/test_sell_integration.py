import ast
import os
from pathlib import Path

from spotify_behavior_engine import SpotifyBehaviorEngine
from spotify_recovered_core import SpotifyRecoveredCore

APP = Path(os.environ.get("APP_PAYLOAD", Path(__file__).resolve().parents[3]))


def fn(path, name):
    text = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_behavior_engine_preserves_safe_outcome(fake_host, monkeypatch):
    engine = SpotifyBehaviorEngine(fake_host)
    monkeypatch.setattr(
        SpotifyRecoveredCore,
        "_spotify_safe_place_step",
        lambda *args, **kwargs: "PENDING",
    )
    assert engine.safe_place_step({}, None, 1.0) == "PENDING"


def test_sell_path_requires_ready_safe_outcome():
    src = fn(APP / "maple_nghia_pro.py", "bot_loop")
    assert "safe_outcome == 'READY'" in src or 'safe_outcome == "READY"' in src
    assert "safe_outcome == 'FAILED'" in src or 'safe_outcome == "FAILED"' in src
    ready = min(i for i in (src.find("safe_outcome == 'READY'"), src.find('safe_outcome == "READY"')) if i >= 0)
    sell = src.index("run_sell_thread")
    assert ready < sell


def test_failed_safe_gate_clears_request_and_never_starts_miumiu():
    src = fn(APP / "maple_nghia_pro.py", "bot_loop")
    marker = "safe_outcome == 'FAILED'" if "safe_outcome == 'FAILED'" in src else 'safe_outcome == "FAILED"'
    assert marker in src
    failed = src.index(marker)
    tail = src[failed:]
    assert "spotify_full_bag_event.clear()" in tail
    ready_marker = "safe_outcome == 'READY'" if "safe_outcome == 'READY'" in tail else 'safe_outcome == "READY"'
    before_ready = tail.split(ready_marker)[0] if ready_marker in tail else tail
    assert "run_sell_thread" not in before_ready


def test_c2_fast_worker_never_calls_watchdog_or_alert_scan():
    src = fn(APP / "maple_nghia_pro.py", "_c2_fast_farm_worker")
    assert "watchdog" not in src.lower()
    assert "captcha" not in src.lower()
    assert "full_bag" not in src.lower()
