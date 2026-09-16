from __future__ import annotations

import os
import sys
from pathlib import Path

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload")).resolve()
sys.path.insert(0, str(APP))


def test_client_capture_region_returns_exact_maple_client():
    from nghia_watchdog_client_capture import client_capture_region

    class FakeUser32:
        def GetClientRect(self, hwnd, ptr):
            rect = ptr._obj
            rect.left = 0
            rect.top = 0
            rect.right = 1280
            rect.bottom = 720
            return 1

        def ClientToScreen(self, hwnd, ptr):
            point = ptr._obj
            point.x = 321
            point.y = 45
            return 1

    assert client_capture_region(FakeUser32(), 1234) == (321, 45, 1280, 720)


def test_client_capture_region_rejects_non_spotify_size():
    from nghia_watchdog_client_capture import client_capture_region

    class FakeUser32:
        def GetClientRect(self, hwnd, ptr):
            rect = ptr._obj
            rect.left = 0
            rect.top = 0
            rect.right = 1279
            rect.bottom = 720
            return 1

        def ClientToScreen(self, hwnd, ptr):
            return 1

    assert client_capture_region(FakeUser32(), 1234) is None


def test_watchdog_capture_uses_client_area_not_desktop_region():
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    start = text.index("    def _spotify_watchdog_capture_frame")
    end = text.index("    def _spotify_watchdog_exact_template_match", start)
    body = text[start:end]
    assert "client_capture_region(user32, hwnd)" in body
    assert 'cfg["region"]' not in body


def test_compact_ui_exposes_timer_and_live_runtime_sync():
    text = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
    for token in (
        "Hẹn giờ bán MiuMiu",
        "variable=self.auto_sell_timer_enabled",
        "textvariable=self.sell_interval_minutes",
        "_on_sell_timer_toggle",
        "_on_sell_interval_change",
        'runtime["auto_sell_timer_enabled"] = enabled',
        'runtime["sell_interval_minutes"] = minutes',
    ):
        assert token in text


def test_spotify_timer_range_is_preserved(monkeypatch):
    from spotify_watchdog import SpotifyWatchdogWorker

    seen = {}

    def fake_uniform(low, high):
        seen["low"] = low
        seen["high"] = high
        return low

    monkeypatch.setattr("spotify_watchdog.random.uniform", fake_uniform)
    delay, source = SpotifyWatchdogWorker(object()).get_next_sell_delay(
        {"sell_interval_minutes": 30.0}
    )
    assert seen == {"low": 20.0, "high": 36.0}
    assert delay == 20.0 * 60.0
    assert source == "spotify_structural"
