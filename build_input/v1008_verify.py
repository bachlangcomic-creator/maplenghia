from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
PORTABLE = ROOT.parent
EXPECTED = {
    "nghia_spotify_nologin.py": "c5e7e915856f0efdd0f027e9d6c415ac53a47fdeda775243f58e585c4c484398",
    "nghia_adaptive_y_ui.py": "7bc0744ffebdb645ebd6e72466aec3890b23fb5e22486be3a78ba5b6794c87ce",
    "maple_nghia_pro.py": "1c0b98fb165278fcd983660c1551eea00d5b8e39a7ec91233e2e5fc117593265",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "nghia_anti_jitter.py": "25ac99c6f5c84d736d641c3c40ac33c3127f4bfd80f6bf46fec09baac899cf0e",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
    "spotify_behavior_engine.py": "8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e",
    "nghia_strategy_v10.py": "f5c1d1c80d8db619c70ec36dbaccc8cdffbd555a63777443dd62767773258108",
    "spotify_watchdog.py": "4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in EXPECTED.items():
    got = sha(ROOT / rel)
    if got != expected:
        raise SystemExit(f"V10.0.8 hash mismatch {rel}: {got} != {expected}")

version = json.loads((PORTABLE / "version.json").read_text(encoding="utf-8"))
if version.get("version") != "10.0.8":
    raise SystemExit(f"V10.0.8 version.json mismatch {version!r}")

ui = (ROOT / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
required = [
    "Nghia Edition V10.0.8",
    "Adaptive Y • không áp dụng cho map này",
    "def _sync_adaptive_y_map_toggle(self):",
    "def _on_adaptive_y_map_toggle(self):",
    "self.runtime_cfg[state.config_key] = enabled",
    "_spotify_reset_c2_adaptive_y_state(clear_anchor=True)",
]
for token in required:
    if token not in ui:
        raise SystemExit(f"V10.0.8 UI token missing: {token}")

print("V1008_VERIFY_OK")
