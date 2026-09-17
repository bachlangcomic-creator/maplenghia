from __future__ import annotations
from pathlib import Path
import base64, hashlib, json, re, sys, zlib

VERSION = "10.0.18"
BASE_HASHES = {
    "spotify_miumiu_sell.py": "2cabfe5db7830d4eed8ed5d0a6e485cf62a0f7352fe79b71ce46fcad3a8f99c6",
    "maple_nghia_pro.py": "7803b58495d717183a896a3ad486fc621875647e49e383ab0f94ec0ecafcb418",
    "nghia_spotify_nologin.py": "1262540b9871c834ca44a919d1e084655814e322b26410d7903d0bfa73a59022",
    "nghia_strategy_v10.py": "3212422ebf60f8a67e948fe6d306f6c5b8d336af9b09a253f7326007a2520947",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
}
NEW_HASHES = {
    "spotify_miumiu_sell.py": "62013cf97b9c005d4d51431347e184f17e429abf72f964835fb322722b20c373",
    "maple_nghia_pro.py": "714c47b0e188dd6dfb12aa72c318639fa87988cec045b9246b4c076d969993f1",
    "nghia_spotify_nologin.py": "bd983513b58025c56ee47cccbed849d716c7d24077c56ec213e4dc87d274c1c2",
}
PATCH_B64 = "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"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_patch(text: str):
    lines = text.splitlines()
    i = 0
    files = {}
    while i < len(lines):
        if not lines[i].startswith("diff --git "):
            i += 1
            continue
        new_path = lines[i].split()[3][2:]
        name = Path(new_path).name
        i += 1
        while i < len(lines) and not lines[i].startswith("@@ "):
            if lines[i].startswith("diff --git "):
                break
            i += 1
        hunks = []
        while i < len(lines) and lines[i].startswith("@@ "):
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", lines[i])
            if not m:
                raise SystemExit(f"bad hunk header: {lines[i]}")
            old_start = int(m.group(1))
            i += 1
            body = []
            while i < len(lines) and not lines[i].startswith("@@ ") and not lines[i].startswith("diff --git "):
                if lines[i].startswith("\\ No newline"):
                    i += 1
                    continue
                body.append(lines[i])
                i += 1
            hunks.append((old_start, body))
        files[name] = hunks
    return files


def apply_hunks(path: Path, hunks):
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    src = raw.decode("utf-8").splitlines()
    out = []
    cursor = 0
    for old_start, body in hunks:
        target = old_start - 1
        if target < cursor:
            raise SystemExit(f"overlapping hunks in {path.name}")
        out.extend(src[cursor:target])
        pos = target
        for entry in body:
            prefix = entry[:1]
            text = entry[1:] if prefix in {" ", "+", "-"} else entry
            if prefix == " ":
                if pos >= len(src) or src[pos] != text:
                    raise SystemExit(f"context mismatch {path.name} line {pos+1}")
                out.append(src[pos]); pos += 1
            elif prefix == "-":
                if pos >= len(src) or src[pos] != text:
                    raise SystemExit(f"remove mismatch {path.name} line {pos+1}")
                pos += 1
            elif prefix == "+":
                out.append(text)
            else:
                raise SystemExit(f"unexpected patch line: {entry}")
        cursor = pos
    out.extend(src[cursor:])
    path.write_bytes((newline.join(out) + newline).encode("utf-8"))


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: v1018_apply.py <portable-root>")
    root = Path(sys.argv[1]).resolve()
    app = root / "app_payload"
    if not app.is_dir():
        raise SystemExit(f"app_payload missing under {root}")
    for name, expected in BASE_HASHES.items():
        path = app / name
        if not path.is_file():
            raise SystemExit(f"V10.0.17 base missing {name}")
        got = sha256(path)
        if got != expected:
            raise SystemExit(f"V10.0.17 base hash mismatch {name}: {got} != {expected}")
    patch = zlib.decompress(base64.b64decode(PATCH_B64)).decode("utf-8")
    parsed = parse_patch(patch)
    for name in NEW_HASHES:
        if name not in parsed:
            raise SystemExit(f"patch missing {name}")
        apply_hunks(app / name, parsed[name])
        got = sha256(app / name)
        if got != NEW_HASHES[name]:
            raise SystemExit(f"V10.0.18 write verification failed {name}: {got}")
    (root / "version.json").write_text(json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8")
    ud = root / "user_data"; ud.mkdir(exist_ok=True)
    (ud / "update_status.json").write_text(json.dumps({
        "latest_version": VERSION,
        "local_version": VERSION,
        "notes": "Nghia V10.0.18: V10.0.17 SAFE ENTRY + Return To Farm base; MiuMiu verified double-click + strict sell confirmation",
        "state": "up_to_date",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("V1018_APPLY_OK")

if __name__ == "__main__":
    main()
