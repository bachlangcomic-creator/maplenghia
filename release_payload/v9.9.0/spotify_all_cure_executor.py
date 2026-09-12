from __future__ import annotations

from pathlib import Path

ALLOWED_EVIDENCE = {'direct', 'high_structural', 'nghia_fallback'}
ALLOWED_OPS = {'find', 'wait_click', 'click_xy', 'paste_text', 'press_key', 'sleep'}


class SpotifyAllCureExecutor:
    def __init__(self, host, asset_gateway):
        self.host = host
        self.asset_gateway = asset_gateway

    def _cancelled(self, cfg):
        fn = getattr(self.host, '_spotify_market_cancelled', None)
        if callable(fn):
            try:
                return bool(fn(cfg))
            except Exception:
                return True
        return bool(cfg.get('cancelled', False)) if isinstance(cfg, dict) else False

    def _validate_action(self, action):
        if not isinstance(action, dict):
            return None
        op = action.get('op')
        if op not in ALLOWED_OPS or action.get('evidence') not in ALLOWED_EVIDENCE:
            return None
        if op in {'find', 'wait_click'}:
            asset = action.get('asset')
            threshold = action.get('threshold')
            if not isinstance(asset, str) or not isinstance(threshold, (int, float)):
                return None
            if not 0.0 <= float(threshold) <= 1.0:
                return None
            try:
                path = Path(self.asset_gateway.path_for(asset))
            except Exception:
                return None
            if not path.is_file():
                return None
            return (op, path, float(threshold))
        if op == 'click_xy':
            x, y = action.get('x'), action.get('y')
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                return None
            return (op, float(x), float(y))
        if op == 'paste_text':
            text = action.get('text')
            if not isinstance(text, str):
                return None
            return (op, text)
        if op == 'press_key':
            key = action.get('key')
            if not isinstance(key, str) or not key.strip():
                return None
            return (op, key)
        if op == 'sleep':
            seconds = action.get('seconds')
            if not isinstance(seconds, (int, float)) or float(seconds) < 0:
                return None
            return (op, float(seconds))
        return None

    def run(self, actions, cfg) -> bool:
        if not isinstance(actions, list) or not actions:
            return False
        compiled = []
        for action in actions:
            item = self._validate_action(action)
            if item is None:
                return False
            compiled.append(item)

        if self._cancelled(cfg):
            return False

        for item in compiled:
            if self._cancelled(cfg):
                return False
            op = item[0]
            if op == 'find':
                ok = self.host._spotify_market_find_asset(item[1], item[2])
            elif op == 'wait_click':
                ok = self.host._spotify_market_wait_click(item[1], item[2], cfg)
            elif op == 'click_xy':
                ok = self.host._spotify_market_click_xy(item[1], item[2], cfg)
            elif op == 'paste_text':
                ok = self.host._spotify_market_paste_text(item[1], cfg)
            elif op == 'press_key':
                ok = self.host._spotify_market_press_key(item[1], cfg)
            elif op == 'sleep':
                ok = self.host._spotify_market_sleep(item[1], cfg)
            else:
                return False
            if ok is False:
                return False
        return True