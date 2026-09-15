import hashlib, importlib.util, sys
from pathlib import Path

ROOT = Path('portable/app_payload').resolve()
PORTABLE = ROOT.parent
sys.path.insert(0, str(ROOT))
EXPECTED = {
    'capture_pool.py': '7b95931f5f2b2a9840d1bfaa921522cddfef53762c358b3aa1f2836226cce741',
    'evidence/main_farm_worker.json': '52385141eb70a955f401ee3decc698fea5d1ee72d914e0696f27f3a3fbc245ec',
    'maple_engine_v2.py': 'a1ed552e9e893dcd20b1c9b40e9cbca1cac20b7c427a9d997cf582c1f532b021',
    'maple_nghia_pro.py': '3ab535e075cfa21b28d5ecf6ddb940db1ae5bc706dd65d82cfc4e1e007dda6c4',
    'nghia_spotify_nologin.py': '401fe85e44aef50ef77cd7fb7895b52b6ba8ff8c3e9f38e2c4ffb2ab8211e032',
    'spotify_all_cure_market.py': 'b3c7c1f7912104e9fd8f3fc12cacc7d26d88335bfec1cecf1d548dca4a742044',
    'spotify_behavior_engine.py': '8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e',
    'spotify_recovered_core.py': '5d0219ea9129a9e5362f4e8a8eb072dd6f8a927dd9ba71db24eaa414afa45c3e',
    'spotify_revive_state.py': '625fa9400713bbd8bb3db65087f2090c5303280508824d0d81a836ba702699fe',
    'spotify_watchdog.py': '4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79',
    'spotify_worker_supervisor.py': '6c39c7b1b79c8364691d9776209c9b362718a1f06cf1cda535f01234af8b8bf2',
    'nghia_strategy_v10.py': 'f5c1d1c80d8db619c70ec36dbaccc8cdffbd555a63777443dd62767773258108',
    'maps.json': '52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d',
}

def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()

for name, expected in EXPECTED.items():
    got = sha(name)
    assert got == expected, (name, got, expected)

version = (PORTABLE / 'version.json').read_text(encoding='utf-8')
assert '"10.0.6"' in version
ui = (ROOT / 'nghia_spotify_nologin.py').read_text(encoding='utf-8')
assert 'Nghia Edition V10.0.6' in ui
assert 'NGHIA_LOCAL_VERSION", "10.0.6"' in ui

spec = importlib.util.spec_from_file_location('core_v1006', ROOT / 'spotify_recovered_core.py')
core_mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core_mod
spec.loader.exec_module(core_mod)
class Host:
    def __init__(self, kind='LEFT_RIGHT'):
        self._kind = kind
        self.spotify_last_loot_time = 1.0
        self.spotify_next_loot_delay = 1.0
    def _spotify_profile_kind(self, cfg):
        return self._kind

core = core_mod.SpotifyRecoveredCore(Host('LEFT_RIGHT'))
exact = {'spotify_runtime_parity_mode': True, 'spotify_loot_enabled': True, 'loot_key': 'Z', 'loot_time': 90}
legacy = dict(exact); legacy['spotify_runtime_parity_mode'] = False
assert core._spotify_generic_loot_due(exact, 100.0) is False
assert core._spotify_generic_loot_due(legacy, 100.0) is True

for module_name, class_name in [
    ('spotify_behavior_engine', 'SpotifyBehaviorEngine'),
    ('nghia_strategy_v10', 'V10StrategyEngine'),
    ('spotify_all_cure_market', 'SpotifyAllCureMarketWorker'),
    ('spotify_watchdog', 'SpotifyWatchdogWorker'),
]:
    spec = importlib.util.spec_from_file_location(f'{module_name}_v1006', ROOT / f'{module_name}.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    assert hasattr(getattr(mod, class_name), 'request_stop'), (module_name, 'request_stop missing')

print('V1006_VERIFY_OK')
