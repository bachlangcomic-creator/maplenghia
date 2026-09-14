import hashlib, importlib.util, sys
from pathlib import Path

ROOT = Path('portable/app_payload').resolve()

def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()

EXPECTED = {
    'spotify_recovered_core.py': '82054ca8057970f86510a7bcc89d1441e5c5d61185a9194d078083aee30ab90a',
    # Exact V10.0.0 hash: C2/B3 Y mechanism is preserved, not rewritten for V10.0.1.
    'maple_nghia_pro.py': '203ac9e103ae3d7e441f7021d15e975e2a3cddaebed4ef8f2a53c17730c0e8bc',
    'nghia_spotify_nologin.py': '525eebc3eab0e8fc4375f935315d400ee4921784c07d240c7594bb68e4af3bbd',
    'nghia_strategy_v10.py': '6066d1ec948b7e9783944a1c2825a033061b1e130fde44b3799783263b1da9b8',
    'maps.json': '52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d',
}
for name, expected in EXPECTED.items():
    got = sha(name)
    assert got == expected, (name, got, expected)

spec = importlib.util.spec_from_file_location('spotify_recovered_core_v1001', ROOT/'spotify_recovered_core.py')
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

class Host:
    def __init__(self):
        self.spotify_recovery_last_trigger = 0.0
        self.spotify_recovery_stage = 0
        self.spotify_recovery_position_lost_since = 100.0
        self.spotify_r54_lost_stage = 0
        self.reacquire_calls = []
        self.recovery_calls = []
        self.classify_calls = []

class RecordingCore(mod.SpotifyRecoveredCore):
    def _spotify_worker_reacquire_reconstructed(self, cfg, lost_for, now):
        self._host.reacquire_calls.append((lost_for, now)); return True
    def _spotify_classify_stuck(self, cfg, map_pos, now, context='farm', target=None):
        self._host.classify_calls.append((context, now)); return 'MINIMAP_LOST'
    def _spotify_recovery(self, cfg, now, reason='stuck'):
        self._host.recovery_calls.append((now, reason))
        self._host.spotify_recovery_stage += 1
        return True

def run_at(lost_for, parity=True):
    host = Host(); core = RecordingCore(host)
    cfg = {'spotify_runtime_parity_mode': parity, 'preview_only': False}
    result = core._spotify_recovery_layer_step(cfg, None, 100.0 + lost_for)
    return host, result

h, r = run_at(3.0, True)
assert r is True and len(h.reacquire_calls) == 1 and h.recovery_calls == [], h.recovery_calls
h, r = run_at(mod.SPOTIFY_RECOVERY_POSITION_HARD, True)
assert r is True and len(h.recovery_calls) == 1, h.recovery_calls
h, r = run_at(3.0, False)
assert r is True and len(h.recovery_calls) == 1, h.recovery_calls

maple = (ROOT/'maple_nghia_pro.py').read_text(encoding='utf-8')
# Preserve the exact V10.0.0 Nghia Y behavior and defaults.
assert 'self.c2_adaptive_y_enabled = tk.BooleanVar(value=True)' in maple
assert 'self.b3_adaptive_y_enabled = tk.BooleanVar(value=False)' in maple
assert 'cfg.get("c2_adaptive_y_enabled", True)' in maple
assert 'cfg.get("b3_adaptive_y_enabled", False)' in maple
load = maple[maple.index('    def load_config('):]
assert '"c2_adaptive_y_enabled", "b3_adaptive_y_enabled"' in load
assert 'getattr(self, name).set(bool(d[name]))' in load

ui = (ROOT/'nghia_spotify_nologin.py').read_text(encoding='utf-8')
assert 'Nghia Edition V10.0.1' in ui
assert 'NGHIA_LOCAL_VERSION", "10.0.1"' in ui

strategy = ROOT/'nghia_strategy_v10.py'
s = importlib.util.spec_from_file_location('nghia_strategy_v10_verify', strategy)
sm = importlib.util.module_from_spec(s); sys.modules[s.name] = sm; s.loader.exec_module(sm)
base = {
 'ENGINE_MODE':'STRATEGY_V10','FARM_TYPE':'PIRATE_ROUTE','COMBAT_MODE':'SPOTIFY_COMBO',
 'TP_MODE':'SPAM_TP_SKILL','LOOT_MODE':'PIRATE_BOTTOM_CUSTOM','LEFT_X':80,'LEFT_Y':190,
 'RIGHT_X':190,'RIGHT_Y':190,'SAFE_PLACE_X':155,'SAFE_PLACE_Y':172,
 'LOOT_BOT_LEFT_X':80,'LOOT_BOT_LEFT_Y':196,'LOOT_BOT_RIGHT_X':189,'LOOT_BOT_RIGHT_Y':196,
 'LOOT_BOT_1_X':105,'LOOT_BOT_1_Y':201,'LOOT_BOT_2_X':170,'LOOT_BOT_2_Y':201,
}
assert sm.custom_bottom_route_points(base,1) == [(80,196),(105,201),(170,201),(189,196)]
assert sm.custom_bottom_route_points(base,-1) == [(189,196),(170,201),(105,201),(80,196)]
print('V1001_VERIFY_OK_Y_PRESERVED')
