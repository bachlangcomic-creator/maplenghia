from __future__ import annotations
from pathlib import Path
import hashlib, sys

EXPECTED = {'spotify_detection_parity.py': 'c50b6bc67dc2ad77bc13104366c8f3ee293febb625cee38a95ebde8bbb9cebc0', 'maple_nghia_pro.py': '16a28bae0dae8a2cbc9720f7ad4db78892f991ed3e206526f8869b68d45c9ac8', 'spotify_watchdog.py': '9748765222d6d820a112241c61cc0fd3e734437da6917069c8a7d047ed2e188c', 'nghia_spotify_nologin.py': 'dd2ddc3eb774c53432ac093460d23f2ce209f3a1876661e94d249c5d061732a5'}
PROTECTED = {
    "spotify_miumiu_sell.py": "62013cf97b9c005d4d51431347e184f17e429abf72f964835fb322722b20c373",
    "nghia_strategy_v10.py": "3212422ebf60f8a67e948fe6d306f6c5b8d336af9b09a253f7326007a2520947",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
    "spotify_pc_alarm.py": "a6c83df75b748e6a6ee398273aa8350ec5138c0f6cb64e77d6c31b1bf42ee3f4",
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('usage: v1019_verify.py <app-payload>')
    app=Path(sys.argv[1])
    for name, expected in {**EXPECTED, **PROTECTED}.items():
        p=app/name
        if not p.is_file(): raise SystemExit(f'missing {name}')
        got=sha(p)
        if got != expected: raise SystemExit(f'hash mismatch {name}: {got} != {expected}')
    ui=(app/'nghia_spotify_nologin.py').read_text(encoding='utf-8')
    if 'V10.0.19' not in ui: raise SystemExit('UI version marker missing')
    parity=(app/'spotify_detection_parity.py').read_text(encoding='utf-8')
    main_text=(app/'maple_nghia_pro.py').read_text(encoding='utf-8')
    watchdog=(app/'spotify_watchdog.py').read_text(encoding='utf-8')
    required_parity=[
        'CAPTCHA_SCALES = (0.90, 0.95, 1.00, 1.05, 1.10)',
        'CAPTCHA_CLEAR_FRAMES = 3',
        'class CaptchaAlertState',
        'class CaptchaTransition',
    ]
    for marker in required_parity:
        if marker not in parity: raise SystemExit(f'missing CAPTCHA parity marker: {marker}')
    for marker in ['_spotify_watchdog_exact_template_match_multiscale', 'CaptchaTransition.APPEARED', 'CaptchaTransition.CLEARED']:
        if marker not in main_text: raise SystemExit(f'missing CAPTCHA integration marker: {marker}')
    if '"captcha")' not in watchdog and '"captcha"' not in watchdog:
        raise SystemExit('watchdog CAPTCHA clear-frame emit path missing')
    if 'QUESTION_CAPTCHA_1_B64' in main_text or 'QUESTION_CAPTCHA_2_B64' in main_text:
        raise SystemExit('QUESTION_CAPTCHA assets must not be wired as independent alarm triggers')
    seller=(app/'spotify_miumiu_sell.py').read_text(encoding='utf-8')
    if 'MIUMIU_OPEN_ATTEMPTS = 2' not in seller or '_click_confirm_and_verify' not in seller:
        raise SystemExit('V10.0.18 MiuMiu strict regression')
    print('V1019_VERIFY_OK')

if __name__ == '__main__': main()
