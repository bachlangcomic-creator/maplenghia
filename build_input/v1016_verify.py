from __future__ import annotations

import hashlib
import sys
from pathlib import Path

APP = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()

# Mutable V10.0.16 controller/strategy files are verified structurally below.
# Protected/original files keep exact byte guards.
EXPECTED = {
    "nghia_spotify_nologin.py": "8b064be4d4318176274350647926c3d592d023d99d707f81c43591d2e5a6ccbf",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "spotify_behavior_engine.py": "8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e",
    "nghia_watchdog_client_capture.py": "80dfabe995f535339d404a332ea5ebde608bb1189984a6d9498206dc9c7c677c",
    "spotify_watchdog.py": "4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79",
    "spotify_pc_alarm.py": "a6c83df75b748e6a6ee398273aa8350ec5138c0f6cb64e77d6c31b1bf42ee3f4",
    "spotify_detection_parity.py": "479a6a5e9d2482fe26d040c5014e0bff61fda75426e8e690c0a173ebb002c2a1",
    "nghia_adaptive_y_ui.py": "7bc0744ffebdb645ebd6e72466aec3890b23fb5e22486be3a78ba5b6794c87ce",
    "nghia_anti_jitter.py": "25ac99c6f5c84d736d641c3c40ac33c3127f4bfd80f6bf46fec09baac899cf0e",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
    "spotify_miumiu_sell.py": "2cabfe5db7830d4eed8ed5d0a6e485cf62a0f7352fe79b71ce46fcad3a8f99c6",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in EXPECTED.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"V10.0.16 protected hash mismatch {rel}: {got} != {expected}")

pro_path = APP / "maple_nghia_pro.py"
strategy_path = APP / "nghia_strategy_v10.py"
pro = pro_path.read_text(encoding="utf-8")
strategy = strategy_path.read_text(encoding="utf-8")
ui = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")

required_pro = [
    '"SAFE_ENTRY": "SAFE ENTRY"',
    '("LEFT", "RIGHT", "SAFE_ENTRY", "SAFE")',
    '"SAFE_ENTRY_X"',
    '"SAFE_ENTRY_Y"',
    'def _spotify_custom_safe_entry_step',
    'entry_outcome = self._spotify_custom_safe_entry_step',
    'self.behavior_engine.core._spotify_jump_up(cfg)',
    'safe_entry=captured["SAFE_ENTRY"]',
    'V10.0.16_RETURN_TO_FARM_AFTER_MIUMIU',
    'request_post_sell_return_to_farm',
    'về X SAFE ENTRY rồi ↓+Jump xuống tầng farm',
]
for needle in required_pro:
    if needle not in pro:
        raise SystemExit(f"V10.0.16 controller marker missing: {needle}")

required_strategy = [
    'safe_entry=None',
    '"SAFE_ENTRY_X"',
    '"SAFE_ENTRY_Y"',
    'def request_post_sell_return_to_farm',
    'def _post_sell_return_to_farm_step',
    'return_to_farm_pending',
    '_spotify_jump_down_reconstructed(cfg)',
    'profile["SAFE_ENTRY_X"]',
    'FALL_RECOVERY_BAND',
]
for needle in required_strategy:
    if needle not in strategy:
        raise SystemExit(f"V10.0.16 strategy marker missing: {needle}")

# FARM RETURN is the separate wrong-floor feature and must remain deferred.
for forbidden in ('"FARM_RETURN_X"', '"FARM_RETURN_Y"', '"FARM_RETURN":', '"FARM RETURN"', "_custom_farm_return_step"):
    if forbidden in pro or forbidden in strategy:
        raise SystemExit(f"Separate FARM RETURN feature must not ship in V10.0.16: {forbidden}")

if "10.0.16" not in ui:
    raise SystemExit("V10.0.16 UI version marker missing")
if "10.0.15" in ui:
    raise SystemExit("stale V10.0.15 UI version marker remains")

print("V1016_SAFE_ENTRY_RETURN_VERIFY_OK")
print("V1016_MUTABLE_SHA maple_nghia_pro.py", sha(pro_path))
print("V1016_MUTABLE_SHA nghia_strategy_v10.py", sha(strategy_path))
