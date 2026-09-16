from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

APP = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
ROOT = APP.parent

UNCHANGED = {
    "maple_nghia_pro.py": "a24fdae1dbc69bb380ec0e3cf8cbc19fb2d34a799a6c782432844e36cdc0c408",
    "nghia_watchdog_client_capture.py": "80dfabe995f535339d404a332ea5ebde608bb1189984a6d9498206dc9c7c677c",
    "spotify_watchdog.py": "4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79",
    "spotify_pc_alarm.py": "a6c83df75b748e6a6ee398273aa8350ec5138c0f6cb64e77d6c31b1bf42ee3f4",
    "spotify_detection_parity.py": "479a6a5e9d2482fe26d040c5014e0bff61fda75426e8e690c0a173ebb002c2a1",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "nghia_adaptive_y_ui.py": "7bc0744ffebdb645ebd6e72466aec3890b23fb5e22486be3a78ba5b6794c87ce",
    "nghia_anti_jitter.py": "25ac99c6f5c84d736d641c3c40ac33c3127f4bfd80f6bf46fec09baac899cf0e",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
    "spotify_behavior_engine.py": "8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
}

CHANGED = {
    "nghia_strategy_v10.py": "4bc8b651eb23e4b3d032e3f48f5c16afbd0969077bbf26576d64bbf8971ca578",
    "nghia_spotify_nologin.py": "ca555f40f3d3bd3efbe0c80636c859ef5208077b9fb78dfc16977b71f03545a5",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in {**UNCHANGED, **CHANGED}.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"hash mismatch {rel}: {got} != {expected}")

strategy = (APP / "nghia_strategy_v10.py").read_text(encoding="utf-8")
for token in (
    "HUMAN_REST_PROBABILITY = 0.02",
    "HUMAN_JUMP_CUMULATIVE = 0.08",
    "rest_ms = random.randint(1000, 1500)",
    "self.human_pause_until = now + (rest_ms / 1000.0)",
    "hold_ms=random.randint(150, 300)",
):
    if token not in strategy:
        raise SystemExit(f"missing V10.0.15 Human Behavior token: {token}")
if "random.uniform(3.0, 5.0)" in strategy:
    raise SystemExit("legacy 3-5 second Human Rest still present")

controller = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
for token in (
    'timer_mode = bool(cfg.get("auto_sell_timer_enabled"))',
    'trigger_due = timer_due if timer_mode else full_bag_due',
    'sell_requested = bool(cfg.get("auto_sell") and cooldown_ok and trigger_due)',
):
    if token not in controller:
        raise SystemExit(f"V10.0.14 Sell Trigger Arbitration regression: {token}")

ui = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
if "V10.0.15" not in ui or "10.0.14" in ui:
    raise SystemExit("compact UI version markers not fully promoted to V10.0.15")

version_file = ROOT / "version.json"
if version_file.exists():
    version = json.loads(version_file.read_text(encoding="utf-8"))
    if version.get("version") != "10.0.15":
        raise SystemExit(f"version.json mismatch: {version}")

print("V1015_VERIFY_OK", {
    "nghia_strategy_v10.py": sha(APP / "nghia_strategy_v10.py"),
    "nghia_spotify_nologin.py": sha(APP / "nghia_spotify_nologin.py"),
    "maple_nghia_pro.py": sha(APP / "maple_nghia_pro.py"),
})
