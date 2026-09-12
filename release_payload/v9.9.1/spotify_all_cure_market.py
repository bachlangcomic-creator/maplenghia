from __future__ import annotations

import json
import threading
from pathlib import Path

from spotify_all_cure_assets import REQUIRED_ALL_CURE_ASSETS, SpotifyAllCureAssetGateway
from spotify_all_cure_executor import SpotifyAllCureExecutor


class SpotifyAllCureMarketWorker:
    def __init__(self, host, evidence_path=None, asset_dir=None):
        self.host = host
        self.generation = 0
        self.thread = None
        self._stop = threading.Event()
        self.evidence_path = Path(evidence_path) if evidence_path else Path(__file__).with_name('evidence') / 'all_cure_market.json'
        if asset_dir is None:
            asset_dir = Path(__file__).resolve().parent.parent / 'user_data' / 'all_cure_images'
        self.asset_dir = Path(asset_dir)
        self.gateway = SpotifyAllCureAssetGateway(self.asset_dir)
        self.executor = SpotifyAllCureExecutor(host, self.gateway)
        self.evidence = self._load_evidence()
        self._last_gate_state = None

    def _load_evidence(self):
        try:
            data = json.loads(self.evidence_path.read_text(encoding='utf-8'))
            if not isinstance(data, dict):
                return {}
            # Read-only V9.8 compatibility view. V9.9 gating still uses the explicit
            # workflow_evidence_ready flag + validated external assets; these legacy
            # fields never make a transaction executable.
            out = dict(data)
            coords = data.get('coordinates') or {}
            out['coordinates'] = {
                name: (record.get('value') if isinstance(record, dict) and 'value' in record else record)
                for name, record in coords.items()
            }
            quantity = data.get('quantity') or {}
            out['buy'] = {
                'quantity': quantity.get('value', 100) if isinstance(quantity, dict) else quantity,
                'complete': False,
            }
            out['sell'] = {'complete': False}
            out['hotkeys'] = {
                'F3': 'run sell_all_cure_loop (recovered reference)',
                'F7': 'toggle continuous all_cure loop (recovered reference)',
            }
            return out
        except (OSError, ValueError, TypeError):
            return {}

    def is_enabled(self, cfg):
        return bool((cfg or {}).get('spotify_all_cure_market_enabled', False))

    def gateway_status(self):
        return self.gateway.validate()

    def workflow_ready(self):
        self.evidence = self._load_evidence()
        return self.evidence.get('workflow_evidence_ready') is True

    def readiness_status(self):
        status = self.gateway_status()
        if status.invalid:
            return 'INVALID', f"invalid={','.join(status.invalid)}"
        if status.missing:
            ready_count = sum(1 for name in REQUIRED_ALL_CURE_ASSETS if self.gateway.path_for(name).is_file())
            return 'MISSING', f'{ready_count}/12; missing={",".join(status.missing)}'
        if not self.workflow_ready():
            return 'INVALID', 'workflow evidence incomplete'
        return 'READY', '12/12 templates + recovered workflow evidence'

    def _gate(self, cfg):
        enabled = self.is_enabled(cfg)
        status = self.gateway_status()
        workflow = self.workflow_ready()
        state = (enabled, status.ready, workflow, status.missing, status.invalid)
        if state != self._last_gate_state:
            self._last_gate_state = state
            log = getattr(self.host, '_log', None)
            if callable(log) and not (enabled and status.ready and workflow):
                reasons = []
                if not enabled:
                    reasons.append('config disabled')
                if not status.ready:
                    if status.missing:
                        reasons.append('missing=' + ','.join(status.missing))
                    if status.invalid:
                        reasons.append('invalid=' + ','.join(status.invalid))
                if not workflow:
                    unresolved = self.evidence.get('unresolved') or []
                    reasons.append('workflow evidence incomplete' + (': ' + ','.join(map(str, unresolved)) if unresolved else ''))
                log('[Spotify All Cure] BLOCKED: ' + '; '.join(reasons))
        return enabled and status.ready and workflow

    def start(self, cfg):
        if self.thread and self.thread.is_alive():
            self.stop()
        self.generation += 1
        generation = self.generation
        self._stop.clear()
        self.thread = threading.Thread(
            target=self._run,
            args=(dict(cfg or {}), generation),
            daemon=True,
            name='Nghia-Spotify-AllCure-Market',
        )
        self.thread.start()

    def stop(self):
        self.generation += 1
        self._stop.set()
        thread = self.thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=0.5)
        self.thread = None

    def _delay(self, name, default):
        try:
            record = (self.evidence.get('loop_delays_seconds') or {}).get(name) or {}
            value = record.get('value', default)
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    def _run(self, initial_cfg, generation):
        cfg = dict(getattr(self.host, 'runtime_cfg', None) or initial_cfg)
        if not self._gate(cfg):
            self._stop.wait()
            return
        while not self._stop.is_set() and generation == self.generation:
            bought = self.request_buy(cfg)
            if bought and self._stop.wait(self._delay('buy_to_sell', 1.0)):
                break
            sold = self.request_sell(cfg)
            if not (bought and sold):
                if self._stop.wait(self._delay('failure_retry', 2.0)):
                    break

    def request_buy(self, cfg):
        if not self._gate(cfg):
            return False
        actions = self.evidence.get('buy_actions')
        return bool(self.host._spotify_market_run_action('buy', actions, cfg))

    def request_sell(self, cfg):
        if not self._gate(cfg):
            return False
        actions = self.evidence.get('sell_actions')
        return bool(self.host._spotify_market_run_action('sell', actions, cfg))
