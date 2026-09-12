import time


class FakeMarketHost:
    def __init__(self):
        self.input_events = []
        self.actions = []
        self.runtime_cfg = None
    def _spotify_market_run_action(self, action_name, evidence, cfg):
        self.actions.append((action_name, evidence, cfg))
        return True
    def _log(self, text):
        self.input_events.append(("log", text))


def test_market_worker_defaults_disabled():
    from spotify_all_cure_market import SpotifyAllCureMarketWorker
    w = SpotifyAllCureMarketWorker(FakeMarketHost())
    assert w.is_enabled({}) is False


def test_unknown_market_action_never_calls_host_bridge():
    from spotify_all_cure_market import SpotifyAllCureMarketWorker
    h = FakeMarketHost(); w = SpotifyAllCureMarketWorker(h)
    assert w.request_buy({"spotify_all_cure_market_enabled": True}) is False
    assert h.actions == []


def test_market_worker_generation_stops_cleanly():
    from spotify_all_cure_market import SpotifyAllCureMarketWorker
    h = FakeMarketHost(); w = SpotifyAllCureMarketWorker(h)
    w.start({"spotify_all_cure_market_enabled": False})
    time.sleep(0.01)
    assert w.thread is not None
    w.stop()
    assert w.thread is None


def test_recovered_market_evidence_is_loaded_but_incomplete_without_external_assets():
    from spotify_all_cure_market import SpotifyAllCureMarketWorker
    w = SpotifyAllCureMarketWorker(FakeMarketHost())
    assert w.evidence["buy"]["quantity"] == 100
    assert w.evidence["coordinates"]["TAB_USE_MARKET"] == [115, 543]
    assert w.evidence["coordinates"]["AVERAGE_PRICE_POSITION"] == [766, 397]
    assert w.evidence["hotkeys"]["F3"].startswith("run sell_all_cure_loop")
    assert w.evidence["hotkeys"]["F7"].startswith("toggle continuous")
    assert w.evidence["buy"]["complete"] is False
    assert w.evidence["sell"]["complete"] is False
    assert w.request_buy({"spotify_all_cure_market_enabled": True}) is False
    assert w.request_sell({"spotify_all_cure_market_enabled": True}) is False
