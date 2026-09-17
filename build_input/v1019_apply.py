from __future__ import annotations
from pathlib import Path
import base64, hashlib, re, sys, zlib

VERSION = "10.0.19"
BASE_HASHES = {'spotify_detection_parity.py': '479a6a5e9d2482fe26d040c5014e0bff61fda75426e8e690c0a173ebb002c2a1', 'maple_nghia_pro.py': '714c47b0e188dd6dfb12aa72c318639fa87988cec045b9246b4c076d969993f1', 'spotify_watchdog.py': '4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79', 'nghia_spotify_nologin.py': 'bd983513b58025c56ee47cccbed849d716c7d24077c56ec213e4dc87d274c1c2', 'spotify_miumiu_sell.py': '62013cf97b9c005d4d51431347e184f17e429abf72f964835fb322722b20c373', 'nghia_strategy_v10.py': '3212422ebf60f8a67e948fe6d306f6c5b8d336af9b09a253f7326007a2520947', 'spotify_recovered_core.py': '7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048', 'spotify_main_farm_orchestrator.py': '1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68', 'maps.json': '52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d', 'spotify_pc_alarm.py': 'a6c83df75b748e6a6ee398273aa8350ec5138c0f6cb64e77d6c31b1bf42ee3f4'}
NEW_HASHES = {'spotify_detection_parity.py': 'c50b6bc67dc2ad77bc13104366c8f3ee293febb625cee38a95ebde8bbb9cebc0', 'maple_nghia_pro.py': '16a28bae0dae8a2cbc9720f7ad4db78892f991ed3e206526f8869b68d45c9ac8', 'spotify_watchdog.py': '9748765222d6d820a112241c61cc0fd3e734437da6917069c8a7d047ed2e188c', 'nghia_spotify_nologin.py': 'dd2ddc3eb774c53432ac093460d23f2ce209f3a1876661e94d249c5d061732a5'}
PATCH_B64 = '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'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_patch(text: str):
    lines = text.splitlines()
    files = {}
    i = 0
    while i < len(lines):
        if not lines[i].startswith('--- '):
            i += 1
            continue
        old_name = lines[i].split(maxsplit=1)[1]
        i += 1
        if i >= len(lines) or not lines[i].startswith('+++ '):
            raise SystemExit('malformed unified diff: missing +++')
        new_name = lines[i].split(maxsplit=1)[1]
        name = Path(new_name[2:] if new_name.startswith('b/') else new_name).name
        i += 1
        hunks = []
        while i < len(lines) and lines[i].startswith('@@ '):
            m = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', lines[i])
            if not m:
                raise SystemExit(f'bad hunk header: {lines[i]}')
            old_start = int(m.group(1))
            i += 1
            body = []
            while i < len(lines) and not lines[i].startswith('@@ ') and not lines[i].startswith('--- '):
                if lines[i].startswith('\\ No newline'):
                    i += 1
                    continue
                body.append(lines[i])
                i += 1
            hunks.append((old_start, body))
        files[name] = hunks
    return files


def apply_hunks(path: Path, hunks) -> None:
    src = path.read_text(encoding='utf-8').splitlines()
    out = []
    cursor = 0
    for old_start, body in hunks:
        target = old_start - 1
        if target < cursor:
            raise SystemExit(f'overlapping hunks in {path.name}')
        out.extend(src[cursor:target])
        pos = target
        for entry in body:
            prefix = entry[:1]
            text = entry[1:] if prefix in (' ', '+', '-') else entry
            if prefix == ' ':
                if pos >= len(src) or src[pos] != text:
                    raise SystemExit(f'context mismatch {path.name} line {pos+1}')
                out.append(src[pos]); pos += 1
            elif prefix == '-':
                if pos >= len(src) or src[pos] != text:
                    raise SystemExit(f'remove mismatch {path.name} line {pos+1}')
                pos += 1
            elif prefix == '+':
                out.append(text)
            else:
                raise SystemExit(f'unexpected patch line in {path.name}: {entry}')
        cursor = pos
    out.extend(src[cursor:])
    path.write_text('\n'.join(out) + '\n', encoding='utf-8')


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('usage: v1019_apply.py <portable-root>')
    root = Path(sys.argv[1]).resolve()
    app = root / 'app_payload'
    if not app.is_dir():
        raise SystemExit(f'app_payload missing under {root}')
    for name, expected in BASE_HASHES.items():
        path = app / name
        if not path.is_file():
            raise SystemExit(f'V10.0.18 base missing {name}')
        got = sha256(path)
        if got != expected:
            raise SystemExit(f'V10.0.18 base hash mismatch {name}: {got} != {expected}')
    patch = zlib.decompress(base64.b64decode(PATCH_B64)).decode('utf-8')
    parsed = parse_patch(patch)
    for name in NEW_HASHES:
        if name not in parsed:
            raise SystemExit(f'patch missing {name}')
        apply_hunks(app / name, parsed[name])
        got = sha256(app / name)
        if got != NEW_HASHES[name]:
            raise SystemExit(f'V10.0.19 write verification failed {name}: {got} != {NEW_HASHES[name]}')
    (root / 'version.json').write_text('{"version":"10.0.19"}\n', encoding='utf-8')
    print('V1019_APPLY_OK')

if __name__ == '__main__':
    main()
