import importlib
import inspect
import time

import pytest


def watchdog_class():
    try:
        return importlib.import_module("spotify_watchdog").SpotifyWatchdogWorker
    except ModuleNotFoundError:
        pytest.fail("spotify_watchdog module is missing")


class Host:
    def __init__(self):
        self.scans = 0
        self.emitted = []
        self.hwnd = 123
        self.runtime_cfg = None

    def _spotify_cached_game_hwnd(self):
        return self.hwnd

    def _spotify_watchdog_capture_frame(self, cfg, hwnd):
        return object()

    def _spotify_watchdog_scan_frame(self, frame, cfg):
        self.scans += 1
        return []

    def _spotify_watchdog_emit(self, result, cfg):
        self.emitted.append(result)

    def _spotify_watchdog_interval(self, cfg):
        return 0.005

    def _log(self, text):
        self.logged = text


def test_watchdog_has_independent_generation_and_stops():
    SpotifyWatchdogWorker = watchdog_class()
    h = Host()
    w = SpotifyWatchdogWorker(h)
    before = w.generation
    w.start({"spotify_watchdog_parity_enabled": True})
    time.sleep(0.03)
    assert w.generation > before and h.scans > 0
    w.stop()
    stopped = w.generation
    time.sleep(0.02)
    assert w.generation == stopped


def test_watchdog_source_has_no_window_enumeration_or_input_calls():
    SpotifyWatchdogWorker = watchdog_class()
    src = inspect.getsource(SpotifyWatchdogWorker)
    for forbidden in (
        "_find_game_window",
        "EnumWindows",
        "set_move(",
        "_press_input_key(",
        "_input_key_down(",
    ):
        assert forbidden not in src
    assert "_spotify_cached_game_hwnd" in src


def test_capture_exception_does_not_escape_worker():
    SpotifyWatchdogWorker = watchdog_class()

    class Broken(Host):
        def _spotify_watchdog_capture_frame(self, cfg, hwnd):
            raise RuntimeError("capture")

    h = Broken()
    w = SpotifyWatchdogWorker(h)
    w.start({"spotify_watchdog_parity_enabled": True})
    time.sleep(0.02)
    w.stop()
    assert hasattr(h, "logged")


def _app_source(name):
    import ast
    import os
    from pathlib import Path

    app = Path(os.environ.get("APP_PAYLOAD", Path(__file__).resolve().parents[3]))
    text = (app / "maple_nghia_pro.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_host_exposes_watchdog_bridges_and_cached_hwnd_only():
    for name in (
        "_spotify_watchdog_capture_frame",
        "_spotify_watchdog_scan_frame",
        "_spotify_watchdog_emit",
        "_spotify_watchdog_interval",
    ):
        assert _app_source(name)
    cap = _app_source("_spotify_watchdog_capture_frame")
    assert "_find_game_window" not in cap
    assert "EnumWindows" not in cap


def test_watchdog_config_is_migration_safe_and_default_on():
    import os
    from pathlib import Path

    app = Path(os.environ.get("APP_PAYLOAD", Path(__file__).resolve().parents[3]))
    text = (app / "maple_nghia_pro.py").read_text(encoding="utf-8")
    assert "spotify_watchdog_parity_enabled" in text
    assert "spotify_watchdog_parity_v1" in text


def test_bot_loop_does_not_run_alert_detectors_synchronously():
    src = _app_source("bot_loop")
    for name in ("dead_template", "dc_template", "captcha_template"):
        assert f'find_best(gray, cfg["{name}"]' not in src
    assert "_spotify_watchdog_scan_frame" not in src


def test_stop_stops_watchdog_before_behavior_engine_shutdown():
    src = _app_source("stop_bot")
    assert src.index("spotify_watchdog.stop()") < src.index("behavior_engine.stop()")


def test_start_launches_watchdog_after_behavior_engine_start():
    src = _app_source("start_bot")
    assert src.index("behavior_engine.start(cfg)") < src.index("spotify_watchdog.start(cfg)")
