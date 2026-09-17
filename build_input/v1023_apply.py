from __future__ import annotations
from pathlib import Path
import base64, hashlib, re, sys, zlib

VERSION = "10.0.23"
BASE_HASHES = {
    'nghia_strategy_v10.py': '64f7815a9fb0397e8b55ed8593548a059791cebec47708e70e93fe6b492530a1',
    'nghia_custom_map_profiles.py': '36042a844b7dac77d62ab60b163e29942226111b467504d72130e12df446662b',
    'maple_nghia_pro.py': '395b8c0c7a12c981905eed4a3ab2d8ffb60be781ffa29e11437b18dff6c6253f',
    'nghia_spotify_nologin.py': 'd378f82ac6bade026dff3bdfac744c17c220029fe9118fb9fa41b3e402f2aa85',
}
NEW_HASHES = {
    'nghia_strategy_v10.py': '8bb3a1b00498b4e19286d91b31251797958774c8b9b5482c4602dd5b9196c5a1',
    'nghia_spotify_nologin.py': 'c080647a228dcf77fb7a7720dced83b59ab38e9fa756851bab0ea96ed8485c89',
}
PATCH_PART_DIR = Path(__file__).resolve().parent / 'patch_parts1023'

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def parse_patch(text: str):
    lines = text.splitlines(); files = {}; i = 0
    while i < len(lines):
        if not lines[i].startswith('--- '): i += 1; continue
        i += 1
        if i >= len(lines) or not lines[i].startswith('+++ '): raise SystemExit('bad patch file header')
        new_path = lines[i].split(maxsplit=1)[1]
        if new_path.startswith('b/'): new_path = new_path[2:]
        name = Path(new_path).name; i += 1; hunks = []
        while i < len(lines) and lines[i].startswith('@@ '):
            m = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', lines[i])
            if not m: raise SystemExit(f'bad hunk header: {lines[i]}')
            old_start = int(m.group(1)); i += 1; body = []
            while i < len(lines) and not lines[i].startswith('@@ ') and not lines[i].startswith('--- '):
                if lines[i].startswith('\\ No newline'): i += 1; continue
                body.append(lines[i]); i += 1
            hunks.append((old_start, body))
        files[name] = hunks
    return files

def apply_hunks(path: Path, hunks):
    src = path.read_bytes().decode('utf-8').splitlines() if path.exists() else []
    out = []; cursor = 0
    for old_start, body in hunks:
        target = max(0, old_start - 1)
        if target < cursor: raise SystemExit(f'overlapping hunks in {path.name}')
        out.extend(src[cursor:target]); pos = target
        for entry in body:
            prefix = entry[:1]; value = entry[1:] if prefix in {' ', '+', '-'} else entry
            if prefix == ' ':
                if pos >= len(src) or src[pos] != value: raise SystemExit(f'context mismatch {path.name} line {pos+1}')
                out.append(src[pos]); pos += 1
            elif prefix == '-':
                if pos >= len(src) or src[pos] != value: raise SystemExit(f'remove mismatch {path.name} line {pos+1}')
                pos += 1
            elif prefix == '+':
                out.append(value)
            else:
                raise SystemExit(f'unexpected patch line: {entry}')
        cursor = pos
    out.extend(src[cursor:])
    path.write_bytes(('\n'.join(out) + '\n').encode('utf-8'))

def main() -> None:
    if len(sys.argv) != 2: raise SystemExit('usage: v1023_apply.py <portable-root>')
    root = Path(sys.argv[1]).resolve(); app = root / 'app_payload'
    if not app.is_dir(): raise SystemExit(f'app_payload missing under {root}')
    for name, expected in BASE_HASHES.items():
        path = app / name
        if not path.is_file(): raise SystemExit(f'V10.0.22 base missing {name}')
        got = sha256(path)
        if got != expected: raise SystemExit(f'V10.0.22 base hash mismatch {name}: {got} != {expected}')
    parts = sorted(PATCH_PART_DIR.glob('part*.txt'))
    if len(parts) != 1: raise SystemExit(f'expected 1 patch part, found {len(parts)}')
    patch_b64 = ''.join(p.read_text(encoding='ascii').strip() for p in parts)
    patch = zlib.decompress(base64.b64decode(patch_b64)).decode('utf-8')
    parsed = parse_patch(patch)
    for name in NEW_HASHES:
        if name not in parsed: raise SystemExit(f'patch missing {name}')
        apply_hunks(app / name, parsed[name])
        got = sha256(app / name)
        if got != NEW_HASHES[name]: raise SystemExit(f'V10.0.23 write verification failed {name}: {got} != {NEW_HASHES[name]}')
    print('V1023_APPLY_OK')

if __name__ == '__main__':
    main()
