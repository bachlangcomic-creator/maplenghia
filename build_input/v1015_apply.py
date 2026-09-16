from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable").resolve()
APP = ROOT / "app_payload"
VERSION = "10.0.15"
OLD_VERSION = "10.0.14"

BASE = {
    "nghia_spotify_nologin.py": "5892f9a3977ea7ee2e0416fdeaf8021e014f3d2912f498f4ceaa843a5668aab2",
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
    "nghia_strategy_v10.py": "e1e256a4abef2d412aa56e481c753fc4debc6485ffed3e7d410a0d707032e1b2",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


for rel, expected in BASE.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.14 base hash {rel}: {got} != {expected}")

strategy_path = APP / "nghia_strategy_v10.py"
s = normalized(strategy_path)
old = '''            self.human_pause_until = now + random.uniform(3.0, 5.0)\n'''
new = '''            rest_ms = random.randint(1000, 1500)\n            self.human_pause_until = now + (rest_ms / 1000.0)\n'''
if s.count(old) != 1:
    raise SystemExit("V10.0.15 Human Rest anchor mismatch")
s = s.replace(old, new, 1)
strategy_path.write_bytes(s.encode("utf-8"))

ui_path = APP / "nghia_spotify_nologin.py"
u = normalized(ui_path)
if "V10.0.14" not in u and "10.0.14" not in u:
    raise SystemExit("V10.0.14 UI version marker missing")
u = u.replace("V10.0.14", "V10.0.15").replace("10.0.14", "10.0.15")
if "10.0.14" in u:
    raise SystemExit("failed to replace all V10.0.14 UI version markers")
ui_path.write_bytes(u.encode("utf-8"))

(ROOT / "version.json").write_text(json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8")

final = {
    "nghia_strategy_v10.py": sha(strategy_path),
    "nghia_spotify_nologin.py": sha(ui_path),
}
print("V1015_PATCH_OK", final)
