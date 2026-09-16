from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
PORTABLE = ROOT.parent

PROTECTED = {
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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in PROTECTED.items():
    got = sha(ROOT / rel)
    if got != expected:
        raise SystemExit(f"V10.0.10 protected hash mismatch {rel}: {got} != {expected}")

version = json.loads((PORTABLE / "version.json").read_text(encoding="utf-8"))
if version.get("version") != "10.0.10":
    raise SystemExit(f"V10.0.10 version.json mismatch {version!r}")

ui = (ROOT / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
for token in (
    "Nghia Edition V10.0.10",
    "Hẹn giờ bán MiuMiu",
    "variable=self.auto_sell_timer_enabled",
    "textvariable=self.sell_interval_minutes",
    "def _on_sell_timer_toggle(self):",
    "def _on_sell_interval_change(self, _event=None):",
):
    if token not in ui:
        raise SystemExit(f"V10.0.10 preserved MiuMiu/version token missing: {token}")

controller = (ROOT / "maple_nghia_pro.py").read_text(encoding="utf-8")
for token in (
    "client_capture_region(user32, hwnd)",
    "SIMPLE Human Behavior",
    "B1/B3 Fall Recovery",
    "Loot Jitter kiểu Spotify",
    "Adaptive Y cho Custom Map",
    "custom_simple_human = tk.BooleanVar(value=False)",
    "custom_fall_recovery = tk.BooleanVar(value=False)",
    "custom_loot_jitter = tk.BooleanVar(value=False)",
    "custom_adaptive_y = tk.BooleanVar(value=False)",
    "custom_simple_human=custom_simple_human.get()",
    "custom_fall_recovery=custom_fall_recovery.get()",
    "custom_loot_jitter=custom_loot_jitter.get()",
    "custom_adaptive_y=custom_adaptive_y.get()",
):
    if token not in controller:
        raise SystemExit(f"V10.0.10 controller token missing: {token}")

start = controller.index("    def _spotify_watchdog_capture_frame")
end = controller.index("    def _spotify_watchdog_exact_template_match", start)
if 'cfg["region"]' in controller[start:end]:
    raise SystemExit("V10.0.10 regressed CAPTCHA capture to desktop region")

strategy = (ROOT / "nghia_strategy_v10.py").read_text(encoding="utf-8")
for token in (
    '"CUSTOM_SIMPLE_HUMAN": bool(custom_simple_human)',
    '"CUSTOM_FALL_RECOVERY": bool(custom_fall_recovery)',
    '"CUSTOM_LOOT_JITTER": bool(custom_loot_jitter)',
    '"CUSTOM_ADAPTIVE_Y": bool(custom_adaptive_y)',
    'random.uniform(0.9, 1.1)',
    'random.uniform(3.0, 5.0)',
    'random.randint(150, 300)',
    'FALL_RECOVERY_CONFIRM = 2.50',
    'def _maybe_human_behavior(self, cfg, now: float)',
    'def _fall_recovery_step(self, cfg, map_pos, now: float)',
):
    if token not in strategy:
        raise SystemExit(f"V10.0.10 strategy token missing: {token}")

if "TOP_START" in strategy or "TOP_END" in strategy:
    raise SystemExit("V10.0.10 Custom Map parity unexpectedly absorbed B3 Top Loot")

print(
    "V1010_VERIFY_OK",
    "strategy=" + sha(ROOT / "nghia_strategy_v10.py"),
    "controller=" + sha(ROOT / "maple_nghia_pro.py"),
    "ui=" + sha(ROOT / "nghia_spotify_nologin.py"),
)
