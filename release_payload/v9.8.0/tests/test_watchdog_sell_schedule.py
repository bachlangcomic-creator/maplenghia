import ast
import inspect
import os
from pathlib import Path

APP = Path(os.environ.get("APP_PAYLOAD", "/mnt/data/v98_task3_check"))


class FakeWatchdogHost:
    def __init__(self):
        self.due = 0
    def _spotify_watchdog_sell_timer_due(self, cfg):
        self.due += 1


def app_source(name):
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_sell_delay_preserves_config_when_exact_bounds_unknown():
    from spotify_watchdog import SpotifyWatchdogWorker
    w = SpotifyWatchdogWorker(FakeWatchdogHost())
    seconds, source = w.get_next_sell_delay({"sell_interval_minutes": 30.0})
    assert seconds == 1800.0
    assert source == "nghia_fallback"


def test_watchdog_owns_timer_state_without_random_uniform():
    from spotify_watchdog import SpotifyWatchdogWorker
    src = inspect.getsource(SpotifyWatchdogWorker)
    assert "last_sell_time" in src
    assert "next_sell_delay" in src
    assert "random.uniform" not in src
    assert "_spotify_watchdog_sell_timer_due" in src


def test_bot_loop_consumes_watchdog_timer_event_instead_of_computing_interval():
    src = app_source("bot_loop")
    assert "spotify_sell_timer_event.is_set()" in src
    assert "sell_interval_minutes" not in src
    assert "timer_due" not in src


def test_host_timer_bridge_only_sets_event():
    src = app_source("_spotify_watchdog_sell_timer_due")
    assert "spotify_sell_timer_event.set()" in src
    assert "run_sell_thread" not in src


def test_safe_sell_clears_watchdog_timer_request():
    src = app_source("bot_loop")
    assert src.count("spotify_sell_timer_event.clear()") >= 2
