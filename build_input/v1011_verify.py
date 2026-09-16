from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sys

APP = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
ROOT = APP.parent

EXPECTED = {
    "nghia_spotify_nologin.py": "bef30874977292e4c7c408c9d69b1ccdce7654c8e571e578a5c4c53f518b6baa",
    "maple_nghia_pro.py": "f5425604caaa24f29b44ae88c62fb4276b519c6f4056c473ad2b4cd9acc4ddc5",
    "nghia_strategy_v10.py": "21b46b689771979094857b1c9da4602e45ca3c335568f3a5af306d751e5fdd99",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "nghia_watchdog_client_capture.py": "80dfabe995f535339d404a332ea5ebde608bb1189984a6d9498206dc9c7c677c",
    "nghia_anti_jitter.py": "25ac99c6f5c84d736d641c3c40ac33c3127f4bfd80f6bf46fec09baac899cf0e",
    "nghia_adaptive_y_ui.py": "7bc0744ffebdb645ebd6e72466aec3890b23fb5e22486be3a78ba5b6794c87ce",
    "spotify_behavior_engine.py": "8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in EXPECTED.items():
    p = APP / rel
    if not p.is_file():
        raise SystemExit(f"missing file {rel}")
    got = sha(p)
    if got != expected:
        raise SystemExit(f"hash mismatch {rel}: {got} != {expected}")

strategy = (APP / "nghia_strategy_v10.py").read_text(encoding="utf-8")
controller = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
ui = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")

for needle in (
    'loot_mode_norm = _norm(loot_mode)',
    'if loot_mode_norm == "PIRATE_BOTTOM_CUSTOM":',
    'PIRATE_BOTTOM_CUSTOM cần đủ 4 tọa độ BOTTOM LOOT',
):
    if needle not in strategy:
        raise SystemExit(f"missing strategy semantic marker: {needle}")

for needle in (
    'def sync_loot_ui',
    'needs_bottom_loot = is_pirate and (not is_v10 or loot_mode.get() == "PIRATE_BOTTOM_CUSTOM")',
    'loot_left = captured["LOOT_LEFT"] if needs_bottom_loot else None',
    'loot_mode_combo.bind("<<ComboboxSelected>>", sync_loot_ui)',
):
    if needle not in controller:
        raise SystemExit(f"missing builder semantic marker: {needle}")

if "10.0.11" not in ui or "10.0.10" in ui:
    raise SystemExit("compact UI version metadata mismatch")

version_path = ROOT / "version.json"
if version_path.is_file():
    version = json.loads(version_path.read_text(encoding="utf-8")).get("version")
    if version != "10.0.11":
        raise SystemExit(f"version.json mismatch {version!r}")

print(
    "V1011_VERIFY_OK",
    f"strategy={EXPECTED['nghia_strategy_v10.py']}",
    f"controller={EXPECTED['maple_nghia_pro.py']}",
    f"ui={EXPECTED['nghia_spotify_nologin.py']}",
)
