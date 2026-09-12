import ast
import os
import textwrap
from pathlib import Path
from types import SimpleNamespace

import spotify_watchdog as wmod

APP = Path(os.environ["APP_PAYLOAD"])


def fn(name):
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_scan_uses_recovered_disconnect_helper_not_alert_threshold():
    src = fn("_spotify_watchdog_scan_frame")
    assert "detect_disconnect_recovered" in src
    dc_slice = src[src.index("detect_disconnect_recovered") :]
    assert "alert_threshold" not in dc_slice.split("full_variants", 1)[0]


def test_disconnect_emit_debounces_and_pauses_before_alert():
    src = fn("_spotify_disconnect_reaction")
    assert "spotify_disconnect_latched" in src
    assert src.index("_spotify_watchdog_request_pause") < src.index("_handle_alert")


def test_disconnect_reaction_runtime_latches_until_nonmatch_reset():
    src = fn("_spotify_disconnect_reaction")
    namespace = {}
    exec("class Carrier:\n" + textwrap.indent(src, "    "), namespace)
    reaction = namespace["Carrier"]._spotify_disconnect_reaction

    class FakeHost:
        def __init__(self):
            self.spotify_disconnect_latched = False
            self.calls = []

        def _spotify_watchdog_request_pause(self, reason, cfg):
            self.calls.append(("pause", reason))
            return True

        def _handle_alert(self, kind, message, cfg):
            self.calls.append(("alert", kind))

    host = FakeHost()
    matched = SimpleNamespace(matched=True)
    clear = SimpleNamespace(matched=False)
    cfg = {"alert_dc": True}

    assert reaction(host, matched, cfg) is True
    assert reaction(host, matched, cfg) is False
    assert host.calls == [("pause", "disconnect"), ("alert", "dc")]

    assert reaction(host, clear, cfg) is False
    assert host.spotify_disconnect_latched is False
    assert reaction(host, matched, cfg) is True
    assert host.calls.count(("alert", "dc")) == 2


def test_watchdog_forwards_disconnect_nonmatch_so_latch_can_reset():
    class StopAfterWait:
        def __init__(self):
            self.stopped = False

        def is_set(self):
            return self.stopped

        def wait(self, _seconds):
            self.stopped = True
            return True

    class WatchHost:
        runtime_cfg = None

        def __init__(self):
            self.emitted = []

        def _spotify_watchdog_interval(self, cfg):
            return 0.001

        def _spotify_cached_game_hwnd(self):
            return 1

        def _spotify_watchdog_capture_frame(self, cfg, hwnd):
            return object()

        def _spotify_watchdog_scan_frame(self, frame, cfg):
            return [SimpleNamespace(kind="disconnect", matched=False)]

        def _spotify_watchdog_emit(self, result, cfg):
            self.emitted.append(result)

        def _log(self, text):
            pass

    host = WatchHost()
    worker = wmod.SpotifyWatchdogWorker(host)
    worker._stop = StopAfterWait()
    worker._run(
        {"spotify_watchdog_parity_enabled": True, "auto_sell_timer_enabled": False},
        worker.generation,
    )

    assert len(host.emitted) == 1
    assert host.emitted[0].kind == "disconnect"
    assert host.emitted[0].matched is False
