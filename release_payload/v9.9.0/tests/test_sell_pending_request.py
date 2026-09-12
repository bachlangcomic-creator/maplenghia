import spotify_watchdog as wmod


class Host:
    def __init__(self):
        self.due = 0

    def _spotify_watchdog_sell_timer_due(self, cfg):
        self.due += 1

    def _log(self, text):
        pass


def test_due_latches_once_until_success(monkeypatch):
    host = Host()
    worker = wmod.SpotifyWatchdogWorker(host)
    worker.last_sell_time = 0.0
    worker.next_sell_delay = 10.0
    monkeypatch.setattr(wmod.time, "monotonic", lambda: 11.0)
    cfg = {"auto_sell_timer_enabled": True}

    worker._sell_schedule_step(cfg)
    worker._sell_schedule_step(cfg)

    assert host.due == 1
    assert worker.sell_due_pending is True


def test_disable_clears_delay_and_pending(monkeypatch):
    host = Host()
    worker = wmod.SpotifyWatchdogWorker(host)
    worker.next_sell_delay = 123.0
    worker.sell_due_pending = True
    monkeypatch.setattr(wmod.time, "monotonic", lambda: 50.0)

    worker._sell_schedule_step({"auto_sell_timer_enabled": False})

    assert worker.next_sell_delay is None
    assert worker.sell_due_pending is False
    assert worker.last_sell_time == 50.0


def test_notify_success_resets_pending_and_next_step_generates_new_delay(monkeypatch):
    host = Host()
    worker = wmod.SpotifyWatchdogWorker(host)
    worker.last_sell_time = 1.0
    worker.next_sell_delay = 10.0
    worker.sell_due_pending = True

    worker.notify_sell_completed(now=100.0)

    assert worker.last_sell_time == 100.0
    assert worker.next_sell_delay is None
    assert worker.sell_due_pending is False

    monkeypatch.setattr(worker, "get_next_sell_delay", lambda cfg: (7.0, "spotify_structural"))
    monkeypatch.setattr(wmod.time, "monotonic", lambda: 100.0)
    worker._sell_schedule_step({"auto_sell_timer_enabled": True})
    assert worker.next_sell_delay == 7.0
    assert host.due == 0
