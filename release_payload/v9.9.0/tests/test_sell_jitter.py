import pytest
import spotify_watchdog as wmod


class Host:
    def _log(self, text):
        pass


def test_sell_jitter_30_minutes_uses_20_to_36(monkeypatch):
    worker = wmod.SpotifyWatchdogWorker(Host())
    seen = {}

    def fake_uniform(a, b):
        seen["bounds"] = (a, b)
        return a

    monkeypatch.setattr(wmod.random, "uniform", fake_uniform)
    delay, source = worker.get_next_sell_delay({"sell_interval_minutes": 30})
    assert seen["bounds"] == (20.0, 36.0)
    assert delay == 1200.0
    assert source == "spotify_structural"


def test_sell_jitter_lower_floor_is_ten_minutes(monkeypatch):
    worker = wmod.SpotifyWatchdogWorker(Host())
    seen = {}

    def fake_uniform(a, b):
        seen["bounds"] = (a, b)
        return b

    monkeypatch.setattr(wmod.random, "uniform", fake_uniform)
    delay, _ = worker.get_next_sell_delay({"sell_interval_minutes": 12})
    assert seen["bounds"] == pytest.approx((10.0, 14.4))
    assert delay == pytest.approx(14.4 * 60.0)


def test_sell_jitter_malformed_zero_clamps_reversed_bounds(monkeypatch):
    worker = wmod.SpotifyWatchdogWorker(Host())
    seen = {}

    def fake_uniform(a, b):
        seen["bounds"] = (a, b)
        assert a <= b
        return a

    monkeypatch.setattr(wmod.random, "uniform", fake_uniform)
    delay, source = worker.get_next_sell_delay({"sell_interval_minutes": 0})
    assert seen["bounds"] == (10.0, 10.0)
    assert delay == 600.0
    assert source == "spotify_structural"
