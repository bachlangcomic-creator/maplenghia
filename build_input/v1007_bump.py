from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from v1007_release import OLD_VERSION, VERSION, bump_ui_text

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable").resolve()
APP = ROOT / "app_payload"

PROTECTED = {
    "maple_nghia_pro.py": "1c0b98fb165278fcd983660c1551eea00d5b8e39a7ec91233e2e5fc117593265",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "nghia_anti_jitter.py": "25ac99c6f5c84d736d641c3c40ac33c3127f4bfd80f6bf46fec09baac899cf0e",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
    "spotify_behavior_engine.py": "8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e",
    "nghia_strategy_v10.py": "f5c1d1c80d8db619c70ec36dbaccc8cdffbd555a63777443dd62767773258108",
    "spotify_watchdog.py": "4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
}
BASE_UI_SHA256 = "f36bf4e270b4a8a4cd04e50f8b766f107d1ea7d6a39fe08e38d48a8fa0767b1c"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in PROTECTED.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"protected V10.0.6 Anti-Jitter file changed before bump: {rel} {got}")

ui_path = APP / "nghia_spotify_nologin.py"
ui_before = ui_path.read_bytes()
if hashlib.sha256(ui_before).hexdigest() != BASE_UI_SHA256:
    raise SystemExit("unexpected V10.0.6 Anti-Jitter UI source hash")
ui_text = ui_before.decode("utf-8")
ui_after = bump_ui_text(ui_text).encode("utf-8")
ui_path.write_bytes(ui_after)

version_path = ROOT / "version.json"
version_obj = json.loads(version_path.read_text(encoding="utf-8"))
if version_obj.get("version") != OLD_VERSION:
    raise SystemExit(f"unexpected base version.json: {version_obj!r}")
version_obj["version"] = VERSION
version_path.write_text(json.dumps(version_obj, indent=2) + "\n", encoding="utf-8")

status_path = ROOT / "user_data" / "update_status.json"
if status_path.is_file():
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["latest_version"] = VERSION
    status["local_version"] = VERSION
    status["notes"] = "Nghia V10.0.7 Anti-Jitter / Hysteresis"
    status["state"] = "up_to_date"
    status_path.write_text(
        json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

print("V1007_SEMANTIC_VERSION_BUMP_OK", hashlib.sha256(ui_after).hexdigest())
