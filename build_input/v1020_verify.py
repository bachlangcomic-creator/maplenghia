from __future__ import annotations
from pathlib import Path
import hashlib, sys

EXPECTED = {
    'maple_nghia_pro.py': '4d62728c0f70afb25c78027491bed6fe2f3cca402e776a1e79608e8183d9ed68',
    'nghia_strategy_v10.py': '3a7a52b51d32c35296132e4f168484cd64618a060a054fd424495cfa2b5cf472',
    'nghia_spotify_nologin.py': '7937f97e60470df658fa505ed3b83d6f646a552e75978872a90ea01d57bd3886',
    'nghia_custom_map_profiles.py': '96884412220ec6d8710d1c2304a49d25950e4534a62695aa83de11f889815f44',
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
    if len(sys.argv) != 2:
        raise SystemExit('usage: v1020_verify.py <app-payload>')
    app=Path(sys.argv[1])
    for name, expected in {**EXPECTED, **PROTECTED}.items():
        p=app/name
        if not p.is_file(): raise SystemExit(f'missing {name}')
        got=sha(p)
        if got != expected: raise SystemExit(f'hash mismatch {name}: {got} != {expected}')
    ui=(app/'nghia_spotify_nologin.py').read_text(encoding='utf-8')
    if 'V10.0.20' not in ui: raise SystemExit('UI version marker missing')
    strategy=(app/'nghia_strategy_v10.py').read_text(encoding='utf-8')
    for marker in ['TWO_FLOOR_ROUTE','build_v10_two_floor_profile','_two_floor_route_step','TWO_FLOOR_RECOVERY','TWO_FLOOR_CHANGE_EACH_LEG']:
        if marker not in strategy: raise SystemExit(f'missing strategy marker: {marker}')
    maple=(app/'maple_nghia_pro.py').read_text(encoding='utf-8')
    for marker in ['TWO FLOOR ROUTE','BOTTOM_LEFT','UP_POINT','Edit Map','Save Changes','Cancel Edit','replace_map_profile']:
        if marker not in maple: raise SystemExit(f'missing UI/edit marker: {marker}')
    print('V1020_VERIFY_OK')

if __name__ == '__main__': main()
