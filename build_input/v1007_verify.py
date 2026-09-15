from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from v1007_release import OLD_VERSION, VERSION

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
PORTABLE = ROOT.parent

EXPECTED = {
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


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


for rel, expected in EXPECTED.items():
    path = ROOT / rel
    assert path.is_file(), f"missing {rel}"
    got = sha(path)
    assert got == expected, (rel, got, expected)

anti = (ROOT / "nghia_anti_jitter.py").read_text(encoding="utf-8")
for forbidden in ("keyDown(", "keyUp(", "press(", "set_move(", "release_move("):
    assert forbidden not in anti, f"Anti-Jitter owns input via {forbidden}"

ui_path = ROOT / "nghia_spotify_nologin.py"
ui_bytes = ui_path.read_bytes()
ui = ui_bytes.decode("utf-8")
assert OLD_VERSION not in ui, f"old semantic version {OLD_VERSION} still present in UI source"
assert f"Nghia Edition V{VERSION}" in ui
assert f'NGHIA_LOCAL_VERSION", "{VERSION}"' in ui
assert "Anti-Jitter / Hysteresis" in ui
assert "variable=self.anti_jitter_enabled" in ui
assert "command=self._on_anti_jitter_toggle" in ui
reverted = ui_bytes.replace(VERSION.encode("ascii"), OLD_VERSION.encode("ascii"))
assert sha_bytes(reverted) == BASE_UI_SHA256, "UI changed beyond the semantic version bump"

maple = (ROOT / "maple_nghia_pro.py").read_text(encoding="utf-8")
assert "self._stop_requested = threading.Event()" in maple
assert "self._stop_cleanup_thread = None" in maple
assert "Đã nhận STOP; đã khóa worker mới, đang nhả input nền." in maple
assert '"anti_jitter_enabled": bool(self.anti_jitter_enabled.get())' in maple

version_path = PORTABLE / "version.json"
version_obj = json.loads(version_path.read_text(encoding="utf-8"))
assert version_obj == {"version": VERSION}, version_obj

print("V1007_VERIFY_OK", sha(ui_path))
