from __future__ import annotations

import ast
import os
import textwrap
from pathlib import Path
from threading import Event

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload")).resolve()


def _extract_method(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    raise AssertionError(f"method not found: {name}")


def _make_stage_harness():
    method = _extract_method(APP / "maple_nghia_pro.py", "_spotify_mainfarm_sell_safe_stage")
    source = "class Harness:\n" + textwrap.indent(textwrap.dedent(method), "    ")
    namespace = {"CONTINUE": "CONTINUE", "STOP_TICK": "STOP_TICK"}
    exec(source, namespace)
    host = namespace["Harness"]()
    host.spotify_full_bag_event = Event()
    host.spotify_sell_timer_event = Event()
    host.last_sell_time = 0.0
    host.spotify_r54_safe_state = "MOVE_SAFE"
    host.spotify_sell_inflight = False
    host._c2_trace_emit = lambda *args, **kwargs: None
    host._log = lambda *args, **kwargs: None
    host.run_sell_thread = lambda cfg: None

    class Core:
        def _spotify_reset_safe_place_state(self):
            pass

    class Engine:
        def __init__(self):
            self.core = Core()
            self.safe_calls = 0
            self.release_calls = 0

        def safe_place_step(self, cfg, map_pos, now):
            self.safe_calls += 1
            return "MOVING"

        def release_inputs(self):
            self.release_calls += 1

    host.behavior_engine = Engine()
    return host


def _cfg(timer_enabled: bool, only_when_full: bool = True):
    return {
        "auto_sell": True,
        "auto_sell_timer_enabled": timer_enabled,
        "sell_only_when_full": only_when_full,
        "sell_cooldown": 0,
        "map_profile": {"SAFE_PLACE_X": 50, "SAFE_PLACE_Y": 20},
    }


def test_timer_mode_ignores_full_bag_until_timer_due():
    host = _make_stage_harness()
    host.spotify_full_bag_event.set()
    assert host._spotify_mainfarm_sell_safe_stage(_cfg(True), (10, 20), 100.0) == "CONTINUE"
    assert host.behavior_engine.safe_calls == 0


def test_timer_mode_ignores_hidden_legacy_always_due_flag():
    host = _make_stage_harness()
    assert host._spotify_mainfarm_sell_safe_stage(
        _cfg(True, only_when_full=False), (10, 20), 100.0
    ) == "CONTINUE"
    assert host.behavior_engine.safe_calls == 0


def test_timer_due_still_preempts_to_safe():
    host = _make_stage_harness()
    host.spotify_sell_timer_event.set()
    assert host._spotify_mainfarm_sell_safe_stage(_cfg(True), (10, 20), 100.0) == "STOP_TICK"
    assert host.behavior_engine.safe_calls == 1


def test_full_bag_mode_still_works_when_timer_disabled():
    host = _make_stage_harness()
    host.spotify_full_bag_event.set()
    assert host._spotify_mainfarm_sell_safe_stage(_cfg(False), (10, 20), 100.0) == "STOP_TICK"
    assert host.behavior_engine.safe_calls == 1


def test_auto_sell_toggle_clears_stale_triggers_and_restarts_timer_schedule():
    method = _extract_method(APP / "nghia_spotify_nologin.py", "_on_auto_sell_toggle")
    source = "class Harness:\n" + textwrap.indent(textwrap.dedent(method), "    ")
    namespace = {}
    exec(source, namespace)

    class Var:
        def get(self):
            return True

    class Watchdog:
        def __init__(self):
            self.reset_calls = 0

        def notify_sell_completed(self):
            self.reset_calls += 1

    host = namespace["Harness"]()
    host.auto_sell = Var()
    host.runtime_cfg = {}
    host.spotify_full_bag_event = Event()
    host.spotify_full_bag_event.set()
    host.spotify_sell_timer_event = Event()
    host.spotify_sell_timer_event.set()
    host.spotify_watchdog = Watchdog()
    host._log = lambda *args, **kwargs: None

    host._on_auto_sell_toggle()

    assert host.runtime_cfg["auto_sell"] is True
    assert not host.spotify_full_bag_event.is_set()
    assert not host.spotify_sell_timer_event.is_set()
    assert host.spotify_watchdog.reset_calls == 1
