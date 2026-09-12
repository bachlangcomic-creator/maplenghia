import ast
import os
import textwrap
from pathlib import Path
from types import SimpleNamespace

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
