from __future__ import annotations
from pathlib import Path
import base64, hashlib, re, sys, zlib

VERSION = "10.0.21"
BASE_HASHES = {
    'nghia_strategy_v10.py': '3a7a52b51d32c35296132e4f168484cd64618a060a054fd424495cfa2b5cf472',
    'nghia_custom_map_profiles.py': '96884412220ec6d8710d1c2304a49d25950e4534a62695aa83de11f889815f44',
    'maple_nghia_pro.py': '4d62728c0f70afb25c78027491bed6fe2f3cca402e776a1e79608e8183d9ed68',
    'nghia_spotify_nologin.py': '7937f97e60470df658fa505ed3b83d6f646a552e75978872a90ea01d57bd3886',
}
NEW_HASHES = {
    'nghia_strategy_v10.py': '366d185c4cb24be44aa911bf2df74cc1979dcb2fbb078a775eaf924248b7b370',
    'nghia_custom_map_profiles.py': '2a597efe900f2f53094e58ae663fded357fe03f10ccd65bb08ac9b0c50a282b8',
    'maple_nghia_pro.py': 'eeace378b61910d75d205d84dc342b7c1090908d2f9cfb67c1cbb4060dc9346b',
    'nghia_spotify_nologin.py': 'c863a6371ee292e60e36a59eff16346694c6885eb000ae86b56e4af8e0c1942d',
}
PATCH_PART_DIR = Path(__file__).resolve().parent / 'patch_parts1021'


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
            prefix = entry[:1]; text = entry[1:] if prefix in {' ', '+', '-'} else entry
            if prefix == ' ':
                if pos >= len(src) or src[pos] != text: raise SystemExit(f'context mismatch {path.name} line {pos+1}')
                out.append(src[pos]); pos += 1
            elif prefix == '-':
                if pos >= len(src) or src[pos] != text: raise SystemExit(f'remove mismatch {path.name} line {pos+1}')
                pos += 1
            elif prefix == '+': out.append(text)
            else: raise SystemExit(f'unexpected patch line: {entry}')
        cursor = pos
    out.extend(src[cursor:])
    path.write_bytes(('\n'.join(out) + '\n').encode('utf-8'))


def main() -> None:
    if len(sys.argv) != 2: raise SystemExit('usage: v1021_apply.py <portable-root>')
    root = Path(sys.argv[1]).resolve(); app = root / 'app_payload'
    if not app.is_dir(): raise SystemExit(f'app_payload missing under {root}')
    for name, expected in BASE_HASHES.items():
        path = app / name
        if not path.is_file(): raise SystemExit(f'V10.0.20 base missing {name}')
        got = sha256(path)
        if got != expected: raise SystemExit(f'V10.0.20 base hash mismatch {name}: {got} != {expected}')
    parts = sorted(PATCH_PART_DIR.glob('part*.txt'))
    if len(parts) != 1: raise SystemExit(f'expected 1 patch part, found {len(parts)}')
    patch_b64 = ''.join(p.read_text(encoding='ascii').strip() for p in parts)
    patch = zlib.decompress(base64.b64decode(patch_b64)).decode('utf-8')
    parsed = parse_patch(patch)
    for name in NEW_HASHES:
        if name not in parsed: raise SystemExit(f'patch missing {name}')
        apply_hunks(app / name, parsed[name])
        got = sha256(app / name)
        if got != NEW_HASHES[name]: raise SystemExit(f'V10.0.21 write verification failed {name}: {got} != {NEW_HASHES[name]}')
    print('V1021_APPLY_OK')

if __name__ == '__main__': main()
