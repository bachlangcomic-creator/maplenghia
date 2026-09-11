import threading


class SpotifyWatchdogWorker:
    def __init__(self, host):
        self.host = host
        self.generation = 0
        self.thread = None
        self._stop = threading.Event()

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
            except Exception as exc:
                self.host._log(f"[Watchdog] scan error: {exc}")
            self._stop.wait(interval)
