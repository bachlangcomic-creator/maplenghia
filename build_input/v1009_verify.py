from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
PORTABLE = ROOT.parent
EXPECTED = {
    "nghia_spotify_nologin.py": "347d2268e7ef850485f069d565ad5025842d3e80efa7b90ce55d32c2f93442b1",
    "maple_nghia_pro.py": "bc44958038e8f94860350879b7676cd47cd532b723bcdd11167867f2f2737286",
    "nghia_watchdog_client_capture.py": "80dfabe995f535339d404a332ea5ebde608bb1189984a6d9498206dc9c7c677c",
    "spotify_watchdog.py": "4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79",
    "spotify_pc_alarm.py": "a6c83df75b748e6a6ee398273aa8350ec5138c0f6cb64e77d6c31b1bf42ee3f4",
    "spotify_detection_parity.py": "479a6a5e9d2482fe26d040c5014e0bff61fda75426e8e690c0a173ebb002c2a1",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "nghia_adaptive_y_ui.py": "7bc0744ffebdb645ebd6e72466aec3890b23fb5e22486be3a78ba5b6794c87ce",
    "nghia_anti_jitter.py": "25ac99c6f5c84d736d641c3c40ac33c3127f4bfd80f6bf46fec09baac899cf0e",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
    "spotify_behavior_engine.py": "8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e",
    "nghia_strategy_v10.py": "f5c1d1c80d8db619c70ec36dbaccc8cdffbd555a63777443dd62767773258108",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in EXPECTED.items():
    got = sha(ROOT / rel)
    if got != expected:
        raise SystemExit(f"V10.0.9 hash mismatch {rel}: {got} != {expected}")

version = json.loads((PORTABLE / "version.json").read_text(encoding="utf-8"))
if version.get("version") != "10.0.9":
    raise SystemExit(f"V10.0.9 version.json mismatch {version!r}")

ui = (ROOT / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
for token in (
    "Nghia Edition V10.0.9",
    "Hẹn giờ bán MiuMiu",
    "variable=self.auto_sell_timer_enabled",
    "textvariable=self.sell_interval_minutes",
    "def _on_sell_timer_toggle(self):",
    "def _on_sell_interval_change(self, _event=None):",
    'runtime["auto_sell_timer_enabled"] = enabled',
    'runtime["sell_interval_minutes"] = minutes',
):
    if token not in ui:
        raise SystemExit(f"V10.0.9 timer UI token missing: {token}")

controller = (ROOT / "maple_nghia_pro.py").read_text(encoding="utf-8")
start = controller.index("    def _spotify_watchdog_capture_frame")
end = controller.index("    def _spotify_watchdog_exact_template_match", start)
capture_body = controller[start:end]
if "client_capture_region(user32, hwnd)" not in capture_body:
    raise SystemExit("V10.0.9 watchdog client capture helper not wired")
if 'cfg["region"]' in capture_body:
    raise SystemExit("V10.0.9 watchdog still captures configured desktop region")

print("V1009_VERIFY_OK")
