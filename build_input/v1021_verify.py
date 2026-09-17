from __future__ import annotations
from pathlib import Path
import hashlib, sys

EXPECTED = {
    'nghia_strategy_v10.py': 'dad6abc868177110457f4abc932971c5ab1422e900e0c607596248de380c98e8',
    'nghia_custom_map_profiles.py': '2a597efe900f2f53094e58ae663fded357fe03f10ccd65bb08ac9b0c50a282b8',
    'maple_nghia_pro.py': 'eeace378b61910d75d205d84dc342b7c1090908d2f9cfb67c1cbb4060dc9346b',
    'nghia_spotify_nologin.py': 'c863a6371ee292e60e36a59eff16346694c6885eb000ae86b56e4af8e0c1942d',
}
PROTECTED = {
    'spotify_detection_parity.py': 'c50b6bc67dc2ad77bc13104366c8f3ee293febb625cee38a95ebde8bbb9cebc0',
    'spotify_watchdog.py': '9748765222d6d820a112241c61cc0fd3e734437da6917069c8a7d047ed2e188c',
    'spotify_miumiu_sell.py': '62013cf97b9c005d4d51431347e184f17e429abf72f964835fb322722b20c373',
    'spotify_recovered_core.py': '7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048',
    'spotify_main_farm_orchestrator.py': '1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68',
    'maps.json': '52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d',
    'spotify_pc_alarm.py': 'a6c83df75b748e6a6ee398273aa8350ec5138c0f6cb64e77d6c31b1bf42ee3f4',
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    if len(sys.argv) != 2: raise SystemExit('usage: v1021_verify.py <app-payload>')
    app = Path(sys.argv[1])
    for name, expected in {**EXPECTED, **PROTECTED}.items():
        p = app / name
        if not p.is_file(): raise SystemExit(f'missing {name}')
        got = sha(p)
        if got != expected: raise SystemExit(f'hash mismatch {name}: {got} != {expected}')
    ui = (app / 'nghia_spotify_nologin.py').read_text(encoding='utf-8')
    if 'V10.0.21' not in ui: raise SystemExit('UI version marker missing')
    strategy = (app / 'nghia_strategy_v10.py').read_text(encoding='utf-8')
    for marker in ['TWO_FLOOR_PASSES_PER_FLOOR', 'two_floor_passes_per_floor', 'two_floor_leg_origin', '_coerce_passes_per_floor']:
        if marker not in strategy: raise SystemExit(f'missing pass-count strategy marker: {marker}')
    maple = (app / 'maple_nghia_pro.py').read_text(encoding='utf-8')
    for marker in ['Số lượt mỗi tầng', 'passes_per_floor', 'Edit Map', 'Save Changes', 'Cancel Edit']:
        if marker not in maple: raise SystemExit(f'missing pass-count UI marker: {marker}')
    if 'Đổi tầng sau mỗi lượt' in maple: raise SystemExit('legacy one-leg checkbox still visible')
    print('V1021_VERIFY_OK')

if __name__ == '__main__': main()
