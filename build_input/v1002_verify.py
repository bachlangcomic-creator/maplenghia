import hashlib, importlib.util, sys
from pathlib import Path

ROOT = Path('portable/app_payload').resolve()
EXPECTED = {
    'capture_pool.py': '7b95931f5f2b2a9840d1bfaa921522cddfef53762c358b3aa1f2836226cce741',
    'evidence/main_farm_worker.json': '52385141eb70a955f401ee3decc698fea5d1ee72d914e0696f27f3a3fbc245ec',
    'maple_engine_v2.py': 'a1ed552e9e893dcd20b1c9b40e9cbca1cac20b7c427a9d997cf582c1f532b021',
    'maple_nghia_pro.py': '020770a55f5f59b4be1ce07c8de28eee15019070146b593c23ed3a1d56349ea4',
    'nghia_spotify_nologin.py': 'aa07672bddd4da5b2a40f8320b31db756844b3db3cb3a4e592927878a4390458',
    'spotify_all_cure_market.py': '734fa741f736a1998ec53aa8835bd3d51ce4002d60138cbb15a789ee0239000e',
    'spotify_recovered_core.py': '72e30e7c5518d31ae100195fc7f4297b9d031af47610a91f5cfc0ea2ab1c3609',
    'spotify_revive_state.py': '625fa9400713bbd8bb3db65087f2090c5303280508824d0d81a836ba702699fe',
    'spotify_watchdog.py': 'b78803f61f17598103e3090387fcb675bf2d1f45a8a9af4157fe7ceb1045c870',
    'spotify_worker_supervisor.py': '6c39c7b1b79c8364691d9776209c9b362718a1f06cf1cda535f01234af8b8bf2',
    'nghia_strategy_v10.py': '6066d1ec948b7e9783944a1c2825a033061b1e130fde44b3799783263b1da9b8',
    'maps.json': '52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d',
}

def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()

for name, expected in EXPECTED.items():
    got = sha(name)
    assert got == expected, (name, got, expected)

ui = (ROOT / 'nghia_spotify_nologin.py').read_text(encoding='utf-8')
assert 'Nghia Edition V10.0.2' in ui
assert 'NGHIA_LOCAL_VERSION", "10.0.2"' in ui

spec = importlib.util.spec_from_file_location('ws_v1002', ROOT / 'spotify_worker_supervisor.py')
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
s = mod.SpotifyWorkerSupervisor(heartbeat_timeout=5.0)
s.record_started(10.0)
s.record_exit(10.1, expected=True)
assert s.expected_stop is False
assert s.observe(10.2, should_run=True, alive=True, heartbeat_at=10.2) == 'HEALTHY'

spec = importlib.util.spec_from_file_location('revive_v1002', ROOT / 'spotify_revive_state.py')
rv = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rv
spec.loader.exec_module(rv)
r = rv.SpotifyReviveState(clear_frames=3, retry_seconds=8.0, max_clicks=3)
assert r.observe(True, 1.0) == 'CLICK'
r.record_click(1.0)
assert r.observe(False, 2.0) == 'WAIT'
assert r.observe(False, 2.1) == 'WAIT'
assert r.observe(False, 2.2) == 'VERIFIED'
print('V1002_VERIFY_OK')
