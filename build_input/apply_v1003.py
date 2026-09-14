from pathlib import Path
import hashlib, json

APP = Path('portable/app_payload')
ROOT = Path('portable')
CORE = APP / 'spotify_recovered_core.py'
UI = APP / 'nghia_spotify_nologin.py'

V1002_CORE_SHA = '72e30e7c5518d31ae100195fc7f4297b9d031af47610a91f5cfc0ea2ab1c3609'
V1002_UI_SHA = 'aa07672bddd4da5b2a40f8320b31db756844b3db3cb3a4e592927878a4390458'
V1003_CORE_SHA = '5d0219ea9129a9e5362f4e8a8eb072dd6f8a927dd9ba71db24eaa414afa45c3e'
V1003_UI_SHA = '61131ccedd816af3c375f583b4e806b620abcaf7c9a866e158e5c059e7ab03bd'

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write_utf8_lf(path: Path, text: str) -> None:
    path.write_bytes(text.replace('\r\n', '\n').encode('utf-8'))

assert sha(CORE) == V1002_CORE_SHA, ('unexpected V10.0.2 core', sha(CORE))
assert sha(UI) == V1002_UI_SHA, ('unexpected V10.0.2 UI', sha(UI))

text = CORE.read_text(encoding='utf-8')
old = '''    def _spotify_generic_loot_due(self, cfg, now):\n        if not self._spotify_loot_enabled(cfg):\n            return False\n'''
new = '''    def _spotify_generic_loot_due(self, cfg, now):\n        # Defense in depth for exact Spotify parity: static/native forensic evidence\n        # does not support a generic Loot-key action for SIMPLE/Bunny-style routes.\n        # Keep legacy generic Loot available only outside exact parity; Pirate routes\n        # continue to own their dedicated route-loot state machines.\n        if (bool(cfg.get("spotify_runtime_parity_mode", True)) and\n                self._spotify_profile_kind(cfg) not in {"PIRATE2", "PIRATE2_1HIT"}):\n            return False\n        if not self._spotify_loot_enabled(cfg):\n            return False\n'''
assert old in text, 'generic loot anchor not found'
write_utf8_lf(CORE, text.replace(old, new, 1))

ui = UI.read_text(encoding='utf-8')
assert '10.0.2' in ui, 'V10.0.2 branding anchor not found'
write_utf8_lf(UI, ui.replace('10.0.2', '10.0.3'))

write_utf8_lf(ROOT / 'version.json', json.dumps({'version': '10.0.3'}, indent=2) + '\n')
ud = ROOT / 'user_data'
ud.mkdir(exist_ok=True)
write_utf8_lf(ud / 'update_status.json', json.dumps({
    'latest_version': '10.0.3',
    'local_version': '10.0.3',
    'notes': 'V10.0.3 Loot Parity Defense: exact Spotify parity blocks generic Loot in the recovered core for SIMPLE/Bunny-style routes; combat/timing and route-owned Loot remain unchanged.',
    'state': 'up_to_date'
}, indent=2, ensure_ascii=False) + '\n')

assert sha(CORE) == V1003_CORE_SHA, ('V10.0.3 core hash mismatch', sha(CORE))
assert sha(UI) == V1003_UI_SHA, ('V10.0.3 UI hash mismatch', sha(UI))
print('V1003_APPLY_OK')
