import json
import threading
from pathlib import Path


class SpotifyAllCureMarketWorker:
    def __init__(self, host, evidence_path=None):
        self.host = host
        self.generation = 0
        self.thread = None
        self._stop = threading.Event()
        self.evidence = self._load_evidence(evidence_path)

    @staticmethod
    def _load_evidence(evidence_path=None):
        path = Path(evidence_path) if evidence_path else Path(__file__).with_name("evidence") / "all_cure_market.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, ValueError, TypeError):
            pass
        return {"buy": None, "sell": None, "hotkeys": {}}

    def is_enabled(self, cfg):
        return bool(cfg.get("spotify_all_cure_market_enabled", False))

    def start(self, cfg):
        if self.thread and self.thread.is_alive():
            self.stop()
        self.generation += 1
        generation = self.generation
        self._stop.clear()
        self.thread = threading.Thread(
            target=self._run,
            args=(dict(cfg), generation),
            daemon=True,
            name="Nghia-Spotify-AllCure-Market",
        )
        self.thread.start()

    def stop(self):
        self.generation += 1
        self._stop.set()
        thread = self.thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=0.5)
        self.thread = None

    def _run(self, initial_cfg, generation):
        cfg = dict(getattr(self.host, "runtime_cfg", None) or initial_cfg)
        if not self.is_enabled(cfg):
            self._stop.wait()
            return
        if not (self._transaction_complete(self.evidence.get("buy")) and self._transaction_complete(self.evidence.get("sell"))):
            self.host._log("[Spotify All Cure] recovered flow is disabled: exact external assets are unavailable.")
            self._stop.wait()
            return
        delays = self.evidence.get("loop_delays_seconds") or {}
        buy_to_sell = float(delays["buy_to_sell"])
        failure_retry = float(delays["failure_retry"])
        while not self._stop.is_set() and generation == self.generation:
            bought = self.request_buy(cfg)
            if bought:
                if self._stop.wait(buy_to_sell):
                    break
            sold = self.request_sell(cfg)
            if not (bought and sold):
                if self._stop.wait(failure_retry):
                    break

    @staticmethod
    def _transaction_complete(record):
        return bool(record and record.get("complete") and record.get("steps"))

    def request_buy(self, cfg):
        if not self.is_enabled(cfg):
            return False
        record = self.evidence.get("buy")
        if not self._transaction_complete(record):
            return False
        return bool(self.host._spotify_market_run_action("buy", record, cfg))

    def request_sell(self, cfg):
        if not self.is_enabled(cfg):
            return False
        record = self.evidence.get("sell")
        if not self._transaction_complete(record):
            return False
        return bool(self.host._spotify_market_run_action("sell", record, cfg))
