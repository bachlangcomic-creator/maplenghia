from __future__ import annotations
from pathlib import Path
import hashlib, sys

EXPECTED = {
    'nghia_strategy_v10.py': '403cfdce5bd33abd2957f3fac0e1e9af075cc37827382eccd2e8c361e85617f5',
    'nghia_custom_map_profiles.py': '36042a844b7dac77d62ab60b163e29942226111b467504d72130e12df446662b',
    'maple_nghia_pro.py': '395b8c0c7a12c981905eed4a3ab2d8ffb60be781ffa29e11437b18dff6c6253f',
    'nghia_spotify_nologin.py': 'c080647a228dcf77fb7a7720dced83b59ab38e9fa756851bab0ea96ed8485c89',
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
    if len(sys.argv) != 2: raise SystemExit('usage: v1023_verify.py <app-payload>')
    app = Path(sys.argv[1])
    for name, expected in {**EXPECTED, **PROTECTED}.items():
        p = app / name
        if not p.is_file(): raise SystemExit(f'missing {name}')
        got = sha(p)
        if got != expected: raise SystemExit(f'hash mismatch {name}: {got} != {expected}')
    ui = (app / 'nghia_spotify_nologin.py').read_text(encoding='utf-8')
    if 'V10.0.23' not in ui or 'TWO FLOOR Natural Combat' not in ui:
        raise SystemExit('V10.0.23 UI marker missing')
    strategy = (app / 'nghia_strategy_v10.py').read_text(encoding='utf-8')
    for marker in [
        'Keep the V10.0.18 run/attack cadence while travelling horizontally',
        'arrived = abs(dx) <= 3.0 and abs(dy) <= 5.0',
        'self.direction = 1 if dx > 0.0 else -1',
        'tick() recognizes this specific FARM -> MOVE',
        'TWO_FLOOR_PASSES_PER_FLOOR',
    ]:
        if marker not in strategy: raise SystemExit(f'missing V10.0.23 strategy marker: {marker}')
    print('V1023_VERIFY_OK')

if __name__ == '__main__':
    main()
