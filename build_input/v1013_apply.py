from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable").resolve()
APP = ROOT / "app_payload"
VERSION = "10.0.13"
OLD_VERSION = "10.0.12"

BASE = {
    "nghia_spotify_nologin.py": "04940254752cf7ffdcca6a49daa1385f6cfd06d71a00d5913116519828b03edc",
    "maple_nghia_pro.py": "b18dbe5dc869f3b12e61c3b35ab0776a8a3a9a3f7d7502f5b0941d032364e611",
    "nghia_watchdog_client_capture.py": "80dfabe995f535339d404a332ea5ebde608bb1189984a6d9498206dc9c7c677c",
    "spotify_watchdog.py": "4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79",
    "spotify_pc_alarm.py": "a6c83df75b748e6a6ee398273aa8350ec5138c0f6cb64e77d6c31b1bf42ee3f4",
    "spotify_detection_parity.py": "479a6a5e9d2482fe26d040c5014e0bff61fda75426e8e690c0a173ebb002c2a1",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "nghia_adaptive_y_ui.py": "7bc0744ffebdb645ebd6e72466aec3890b23fb5e22486be3a78ba5b6794c87ce",
    "nghia_anti_jitter.py": "25ac99c6f5c84d736d641c3c40ac33c3127f4bfd80f6bf46fec09baac899cf0e",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
    "spotify_behavior_engine.py": "8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e",
    "nghia_strategy_v10.py": "21b46b689771979094857b1c9da4602e45ca3c335568f3a5af306d751e5fdd99",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
}

FINAL = {
    "nghia_spotify_nologin.py": "6a06448e65ae79b0cfdb7af61ff3322f248bb2b6675a21fde8f11e6ba21b228d",
    "nghia_strategy_v10.py": "7d8c9f467a86b140cf528cffdd63091be0173be8433bf805e7d970857215d92b",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


for rel, expected in BASE.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.12 base hash {rel}: {got} != {expected}")

strategy_path = APP / "nghia_strategy_v10.py"
s = normalized(strategy_path)

import_anchor = "from typing import Any, Mapping, Optional, Tuple\n"
if s.count(import_anchor) != 1:
    raise SystemExit("V10.0.13 strategy import anchor mismatch")
s = s.replace(
    import_anchor,
    import_anchor + "\nfrom spotify_main_farm_orchestrator import STOP_TICK\n",
    1,
)

helper_anchor = '''    def tick(self, cfg: Mapping[str, Any], map_pos, now: float) -> bool:\n'''
helper = '''    def _sell_safe_step(self, cfg: Mapping[str, Any], map_pos, now: float) -> bool:\n        sell_lock = getattr(self.host, "sell_lock", None)\n        lock_held = bool(sell_lock is not None and callable(getattr(sell_lock, "locked", None)) and sell_lock.locked())\n        if bool(getattr(self.host, "spotify_sell_inflight", False)) or lock_held:\n            self.release_inputs()\n            return True\n        stage = getattr(self.host, "_spotify_mainfarm_sell_safe_stage", None)\n        if not callable(stage):\n            return False\n        return stage(cfg, map_pos, now, owner="V10_STRATEGY") == STOP_TICK\n\n'''
if s.count(helper_anchor) != 1:
    raise SystemExit("V10.0.13 tick helper anchor mismatch")
s = s.replace(helper_anchor, helper + helper_anchor, 1)

old = '''        if map_pos is None:\n            self.release_inputs()\n            return False\n        if self.loot_state != "FARM":\n            return self._custom_loot_step(cfg, map_pos, now)\n'''
new = '''        if map_pos is None:\n            self.release_inputs()\n            return False\n        if self._sell_safe_step(cfg, map_pos, now):\n            return True\n        if self.loot_state != "FARM":\n            return self._custom_loot_step(cfg, map_pos, now)\n'''
if s.count(old) != 1:
    raise SystemExit("V10.0.13 sell-safe tick anchor mismatch")
s = s.replace(old, new, 1)
strategy_path.write_text(s, encoding="utf-8")

ui_path = APP / "nghia_spotify_nologin.py"
u = normalized(ui_path)
if "V10.0.12" not in u and "10.0.12" not in u:
    raise SystemExit("V10.0.12 UI version marker missing")
u = u.replace("V10.0.12", "V10.0.13").replace("10.0.12", "10.0.13")
if "10.0.12" in u:
    raise SystemExit("failed to replace all V10.0.12 UI version markers")
ui_path.write_text(u, encoding="utf-8")

(ROOT / "version.json").write_text(json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8")

for rel, expected in FINAL.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.13 final hash {rel}: {got} != {expected}")

print("V1013_PATCH_OK", FINAL)
