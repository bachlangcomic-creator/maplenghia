from dataclasses import is_dataclass
import inspect
import time


def test_watchdog_event_contract():
    from spotify_watchdog import SpotifyWatchdogEvent
    e = SpotifyWatchdogEvent("captcha", None, "spotify_exact", {})
    assert is_dataclass(e)
    assert e.kind == "captcha"
    assert e.source == "spotify_exact"
    assert e.payload == {}


def test_watchdog_worker_never_enumerates_or_injects_input():
    from spotify_watchdog import SpotifyWatchdogWorker
    src = inspect.getsource(SpotifyWatchdogWorker)
    for forbidden in ("_find_game_window", "EnumWindows", "set_move(", "_press_input_key(", "_input_key_down("):
        assert forbidden not in src
    assert "_spotify_cached_game_hwnd" in src


class Host:
    def __init__(self):
        self.scans = 0
        self.runtime_cfg = None
    def _spotify_cached_game_hwnd(self): return 123
    def _spotify_watchdog_capture_frame(self, cfg, hwnd): return object()
    def _spotify_watchdog_scan_frame(self, frame, cfg): self.scans += 1; return []
    def _spotify_watchdog_emit(self, result, cfg): pass
    def _spotify_watchdog_interval(self, cfg): return 0.005
    def _log(self, text): self.logged = text


def test_watchdog_generation_still_stops_cleanly():
    from spotify_watchdog import SpotifyWatchdogWorker
    h = Host(); w = SpotifyWatchdogWorker(h)
    w.start({"spotify_watchdog_parity_enabled": True})
    time.sleep(0.02)
    assert h.scans > 0
    w.stop()
    g = w.generation
    time.sleep(0.01)
    assert w.generation == g
