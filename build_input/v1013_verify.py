from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

APP = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
ROOT = APP.parent

EXPECTED = {
    "nghia_spotify_nologin.py": "6a06448e65ae79b0cfdb7af61ff3322f248bb2b6675a21fde8f11e6ba21b228d",
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
    "nghia_strategy_v10.py": "e1e256a4abef2d412aa56e481c753fc4debc6485ffed3e7d410a0d707032e1b2",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in EXPECTED.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"hash mismatch {rel}: {got} != {expected}")

strategy = (APP / "nghia_strategy_v10.py").read_text(encoding="utf-8")
required = [
    "def _sell_safe_step",
    'getattr(self.host, "spotify_sell_inflight", False)',
    'getattr(self.host, "sell_lock", None)',
    'getattr(self.host, "_spotify_mainfarm_sell_safe_stage", None)',
    'owner="V10_STRATEGY"',
    '== "STOP_TICK"',
    "if self._sell_safe_step(cfg, map_pos, now):",
]
for token in required:
    if token not in strategy:
        raise SystemExit(f"missing V10.0.13 sell-safe token: {token}")

tick_pos = strategy.index("    def tick(")
sell_call = strategy.index("if self._sell_safe_step(cfg, map_pos, now):", tick_pos)
loot_call = strategy.index('if self.loot_state != "FARM":', tick_pos)
farm_call = strategy.index("edge_hit = self._farm_route_step", tick_pos)
if not (tick_pos < sell_call < loot_call < farm_call):
    raise SystemExit("SELL_SAFE must preempt Custom Map loot/farm")

controller = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
for token in (
    "def _spotify_mainfarm_sell_safe_stage",
    "spotify_sell_timer_event.is_set()",
    "SAFE_PLACE_X",
    "self.run_sell_thread(cfg)",
):
    if token not in controller:
        raise SystemExit(f"existing MiuMiu SELL_SAFE contract missing: {token}")

ui = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
if "V10.0.13" not in ui or "10.0.12" in ui:
    raise SystemExit("compact UI version markers not fully promoted to V10.0.13")

version_file = ROOT / "version.json"
if version_file.exists():
    version = json.loads(version_file.read_text(encoding="utf-8"))
    if version.get("version") != "10.0.13":
        raise SystemExit(f"version.json mismatch: {version}")

print("V1013_VERIFY_OK", {k: sha(APP / k) for k in ("nghia_strategy_v10.py", "nghia_spotify_nologin.py")})
