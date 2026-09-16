from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

APP = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
ROOT = APP.parent

EXPECTED = {
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


for rel, expected in EXPECTED.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"hash mismatch {rel}: {got} != {expected}")

controller = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
for token in (
    'timer_mode = bool(cfg.get("auto_sell_timer_enabled"))',
    'timer_due = self.spotify_sell_timer_event.is_set()',
    'full_bag_due = self.spotify_full_bag_event.is_set()',
    'trigger_due = timer_due if timer_mode else full_bag_due',
    'sell_requested = bool(cfg.get("auto_sell") and cooldown_ok and trigger_due)',
):
    if token not in controller:
        raise SystemExit(f"missing V10.0.14 trigger arbitration token: {token}")
if 'condition_due = (not cfg.get("sell_only_when_full"))' in controller:
    raise SystemExit("legacy unconditional sell trigger still present")

ui = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
for token in (
    "def _on_auto_sell_toggle",
    'runtime["auto_sell"] = enabled',
    '("spotify_full_bag_event", "spotify_sell_timer_event")',
    'getattr(watchdog, "notify_sell_completed", None)',
    "command=self._on_auto_sell_toggle",
):
    if token not in ui:
        raise SystemExit(f"missing V10.0.14 compact UI reset token: {token}")
if "V10.0.14" not in ui or "10.0.13" in ui:
    raise SystemExit("compact UI version markers not fully promoted to V10.0.14")

strategy = (APP / "nghia_strategy_v10.py").read_text(encoding="utf-8")
for token in (
    "def _sell_safe_step",
    'getattr(self.host, "spotify_sell_inflight", False)',
    'getattr(self.host, "sell_lock", None)',
    'owner="V10_STRATEGY"',
    "if self._sell_safe_step(cfg, map_pos, now):",
):
    if token not in strategy:
        raise SystemExit(f"V10.0.13 Custom Map sell-safe regression: {token}")

version_file = ROOT / "version.json"
if version_file.exists():
    version = json.loads(version_file.read_text(encoding="utf-8"))
    if version.get("version") != "10.0.14":
        raise SystemExit(f"version.json mismatch: {version}")

print("V1014_VERIFY_OK", {
    "maple_nghia_pro.py": sha(APP / "maple_nghia_pro.py"),
    "nghia_spotify_nologin.py": sha(APP / "nghia_spotify_nologin.py"),
    "nghia_strategy_v10.py": sha(APP / "nghia_strategy_v10.py"),
})
