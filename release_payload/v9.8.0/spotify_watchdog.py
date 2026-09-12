from dataclasses import dataclass, field
import threading
import time


@dataclass(frozen=True)
class SpotifyWatchdogEvent:
    kind: str
    detection: object | None
    source: str
    payload: dict = field(default_factory=dict)


class SpotifyWatchdogWorker:
    def __init__(self, host):
        self.host = host
        self.generation = 0
        self.thread = None
        self._stop = threading.Event()
        self.last_sell_time = time.monotonic()
        self.next_sell_delay = None

    def start(self, cfg):
        if self.thread and self.thread.is_alive():
            self.stop()
        self.generation += 1
        generation = self.generation
        self._stop.clear()
        self.last_sell_time = time.monotonic()
        self.next_sell_delay = None
        self.thread = threading.Thread(
            target=self._run,
            args=(dict(cfg), generation),
            daemon=True,
            name="Nghia-Spotify-Watchdog",
        )
        self.thread.start()

    def stop(self):
        self.generation += 1
        self._stop.set()
        thread = self.thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=0.5)
        self.thread = None

    def get_next_sell_delay(self, cfg):
        minutes = max(0.0, float(cfg.get("sell_interval_minutes", 30.0)))
        return minutes * 60.0, "nghia_fallback"

    def notify_sell_completed(self, now=None):
        self.last_sell_time = time.monotonic() if now is None else float(now)
        self.next_sell_delay = None

    def _sell_schedule_step(self, cfg):
        if not cfg.get("auto_sell_timer_enabled"):
            self.next_sell_delay = None
            self.last_sell_time = time.monotonic()
            return
        if self.next_sell_delay is None:
            self.next_sell_delay, _source = self.get_next_sell_delay(cfg)
        now = time.monotonic()
        if now - self.last_sell_time < self.next_sell_delay:
            return
        self.host._spotify_watchdog_sell_timer_due(cfg)
        self.last_sell_time = now
        self.next_sell_delay, _source = self.get_next_sell_delay(cfg)

    def _run(self, initial_cfg, generation):
        while not self._stop.is_set() and generation == self.generation:
            cfg = dict(getattr(self.host, "runtime_cfg", None) or initial_cfg)
            interval = max(0.001, float(self.host._spotify_watchdog_interval(cfg)))
            if not cfg.get("spotify_watchdog_parity_enabled", True):
                self._stop.wait(interval)
                continue
            try:
                hwnd = self.host._spotify_cached_game_hwnd()
                if hwnd:
                    frame = self.host._spotify_watchdog_capture_frame(cfg, hwnd)
                    if frame is not None:
                        for result in self.host._spotify_watchdog_scan_frame(frame, cfg):
                            if result.matched:
                                self.host._spotify_watchdog_emit(result, cfg)
                self._sell_schedule_step(cfg)
            except Exception as exc:
                self.host._log(f"[Watchdog] scan error: {exc}")
            self._stop.wait(interval)
