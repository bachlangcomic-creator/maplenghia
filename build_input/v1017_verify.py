from __future__ import annotations

import hashlib
import sys
from pathlib import Path

APP = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


pro_path = APP / "maple_nghia_pro.py"
strategy_path = APP / "nghia_strategy_v10.py"
ui_path = APP / "nghia_spotify_nologin.py"
maps_path = APP / "maps.json"
for path in (pro_path, strategy_path, ui_path, maps_path):
    if not path.is_file():
        raise SystemExit(f"V10.0.17 missing required file: {path.name}")

pro = pro_path.read_text(encoding="utf-8")
strategy = strategy_path.read_text(encoding="utf-8")
ui = ui_path.read_text(encoding="utf-8")

required_pro = [
    "V10.0.17_SAFE_ENTRY_RETURN",
    '"SAFE_ENTRY": "SAFE ENTRY"',
    '("LEFT", "RIGHT", "SAFE_ENTRY", "SAFE")',
    '"SAFE_ENTRY_X"',
    '"SAFE_ENTRY_Y"',
    "def _spotify_custom_safe_entry_step",
    "self.behavior_engine.core._spotify_jump_up(cfg)",
    'safe_entry=captured["SAFE_ENTRY"]',
    "request_post_sell_return_to_farm",
    "↓+Jump xuống tầng farm",
]
for needle in required_pro:
    if needle not in pro:
        raise SystemExit(f"V10.0.17 controller marker missing: {needle}")

required_strategy = [
    "V10.0.17_SAFE_ENTRY_RETURN",
    "safe_entry: Optional[Tuple[float, float]] = None",
    '"SAFE_ENTRY_X"',
    '"SAFE_ENTRY_Y"',
    "def request_post_sell_return_to_farm",
    "def _post_sell_return_to_farm_step",
    "return_to_farm_pending",
    "_spotify_jump_down_reconstructed(cfg)",
    "resolved.safe_entry[0]",
]
for needle in required_strategy:
    if needle not in strategy:
        raise SystemExit(f"V10.0.17 strategy marker missing: {needle}")

for forbidden in ('"FARM_RETURN_X"', '"FARM_RETURN_Y"', '"FARM_RETURN":', '"FARM RETURN"', "_custom_farm_return_step"):
    if forbidden in pro or forbidden in strategy:
        raise SystemExit(f"Separate FARM RETURN feature must not ship in V10.0.17: {forbidden}")

if "10.0.17" not in ui:
    raise SystemExit("V10.0.17 UI version marker missing")
if "10.0.15" in ui:
    raise SystemExit("stale V10.0.15 UI version marker remains")

maps_expected = "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d"
maps_got = sha(maps_path)
if maps_got != maps_expected:
    raise SystemExit(f"bundled maps.json changed: {maps_got} != {maps_expected}")

print("V1017_SAFE_ENTRY_RETURN_VERIFY_OK")
print("V1017_MUTABLE_SHA maple_nghia_pro.py", sha(pro_path))
print("V1017_MUTABLE_SHA nghia_strategy_v10.py", sha(strategy_path))
print("V1017_MUTABLE_SHA nghia_spotify_nologin.py", sha(ui_path))
print("V1017_PROTECTED_SHA maps.json", maps_got)
