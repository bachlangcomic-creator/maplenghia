from __future__ import annotations

from pathlib import Path
import hashlib, sys

EXPECTED = {'spotify_miumiu_sell.py': '62013cf97b9c005d4d51431347e184f17e429abf72f964835fb322722b20c373', 'maple_nghia_pro.py': '714c47b0e188dd6dfb12aa72c318639fa87988cec045b9246b4c076d969993f1', 'nghia_spotify_nologin.py': 'bd983513b58025c56ee47cccbed849d716c7d24077c56ec213e4dc87d274c1c2'}
PROTECTED = {
    "nghia_strategy_v10.py": "3212422ebf60f8a67e948fe6d306f6c5b8d336af9b09a253f7326007a2520947",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: v1018_verify.py <app-payload>")
    app=Path(sys.argv[1])
    for name, expected in {**EXPECTED, **PROTECTED}.items():
        p=app/name
        if not p.is_file():
            raise SystemExit(f"missing {name}")
        got=sha(p)
        if got != expected:
            raise SystemExit(f"hash mismatch {name}: {got} != {expected}")
    text=(app/'nghia_spotify_nologin.py').read_text(encoding='utf-8')
    if 'V10.0.18' not in text:
        raise SystemExit('UI version marker missing')
    seller=(app/'spotify_miumiu_sell.py').read_text(encoding='utf-8')
    required=[
        'MIUMIU_OPEN_ATTEMPTS = 2',
        'click_count=2',
        '_click_confirm_and_verify',
        'return result in {PIRATE_SELL_SOLD, PIRATE_SELL_EMPTY}',
    ]
    for marker in required:
        if marker not in seller:
            raise SystemExit(f'missing seller marker: {marker}')
    if 'return sold_any or True' in seller:
        raise SystemExit('false-success pattern still present')
    print('V1018_VERIFY_OK')

if __name__ == '__main__':
    main()
