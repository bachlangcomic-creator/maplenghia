from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

APP = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
ROOT = APP.parent

UNCHANGED = {
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
    "nghia_strategy_v10.py": "d10065f38a10140c5613dbf4ff8d65ad35a1ce8ee07564720199af6e0906943d",
    "maple_nghia_pro.py": "ecb4486fafc98e0f9939f924e0f64ad18960958638d68723b0004344b8efeb38",
    "nghia_spotify_nologin.py": "8b064be4d4318176274350647926c3d592d023d99d707f81c43591d2e5a6ccbf",
}

SELL_SAFE_STAGE_SHA256 = "2bc6ad4ebeee44c7266196cad789dee05301621b8e2e2e83163b364144774be0"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in {**UNCHANGED, **CHANGED}.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"hash mismatch {rel}: {got} != {expected}")

strategy = (APP / "nghia_strategy_v10.py").read_text(encoding="utf-8")
for token in (
    'safe_entry: Optional[Tuple[float, float]] = None',
    'farm_return: Optional[Tuple[float, float]] = None',
    '"SAFE_ENTRY_X"',
    '"FARM_RETURN_X"',
    'def _sell_trigger_due(',
    'self.host.behavior_engine.core._spotify_jump_up(cfg)',
    'self.host.behavior_engine.core._spotify_jump_down_reconstructed(cfg)',
    'def _upper_floor_return_step(',
    'rest_ms = random.randint(1000, 1500)',
):
    if token not in strategy:
        raise SystemExit(f"missing V10.0.16 strategy token: {token}")

controller = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
for token in (
    '"SAFE_ENTRY": "SAFE ENTRY"',
    '"FARM_RETURN": "FARM RETURN"',
    'farm_optional_button_widgets',
    'safe_entry=captured["SAFE_ENTRY"]',
    'farm_return=captured["FARM_RETURN"]',
    'timer_mode = bool(cfg.get("auto_sell_timer_enabled"))',
    'trigger_due = timer_due if timer_mode else full_bag_due',
):
    if token not in controller:
        raise SystemExit(f"missing V10.0.16 controller token: {token}")

start = controller.index("    def _spotify_mainfarm_sell_safe_stage")
end = controller.index("    def _spotify_mainfarm_pet_stage", start)
sell_stage_sha = hashlib.sha256(controller[start:end].encode("utf-8")).hexdigest()
if sell_stage_sha != SELL_SAFE_STAGE_SHA256:
    raise SystemExit(f"shared sell-safe stage changed: {sell_stage_sha}")

ui = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
if "V10.0.16" not in ui or "10.0.15" in ui:
    raise SystemExit("compact UI version markers not fully promoted to V10.0.16")

version_file = ROOT / "version.json"
if version_file.exists():
    version = json.loads(version_file.read_text(encoding="utf-8"))
    if version.get("version") != "10.0.16":
        raise SystemExit(f"version.json mismatch: {version}")

print("V1016_VERIFY_OK", {
    "nghia_strategy_v10.py": sha(APP / "nghia_strategy_v10.py"),
    "maple_nghia_pro.py": sha(APP / "maple_nghia_pro.py"),
    "nghia_spotify_nologin.py": sha(APP / "nghia_spotify_nologin.py"),
    "shared_sell_safe_stage_sha256": sell_stage_sha,
    "maps.json": sha(APP / "maps.json"),
})
