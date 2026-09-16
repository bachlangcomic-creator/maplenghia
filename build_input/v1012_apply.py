from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable").resolve()
APP = ROOT / "app_payload"
VERSION = "10.0.12"
OLD_VERSION = "10.0.11"

BASE = {
    "nghia_spotify_nologin.py": "bef30874977292e4c7c408c9d69b1ccdce7654c8e571e578a5c4c53f518b6baa",
    "maple_nghia_pro.py": "f5425604caaa24f29b44ae88c62fb4276b519c6f4056c473ad2b4cd9acc4ddc5",
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
    "nghia_spotify_nologin.py": "04940254752cf7ffdcca6a49daa1385f6cfd06d71a00d5913116519828b03edc",
    "maple_nghia_pro.py": "b18dbe5dc869f3b12e61c3b35ab0776a8a3a9a3f7d7502f5b0941d032364e611",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


for rel, expected in BASE.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.11 base hash {rel}: {got} != {expected}")

controller_path = APP / "maple_nghia_pro.py"
c = normalized(controller_path)

anchor = '''    def _spotify_watchdog_scan_frame(self, frame, cfg):\n'''
helper = '''    @staticmethod\n    def _preview_box_or_none(value):\n        if isinstance(value, (tuple, list)) and len(value) >= 5:\n            return value\n        return None\n\n'''
if c.count(anchor) != 1:
    raise SystemExit("watchdog scan method anchor mismatch")
c = c.replace(anchor, helper + anchor, 1)

old = '''            if recovered is not None and recovered.matched:\n                setattr(self, cache_name, recovered)\n                continue\n'''
new = '''            if recovered is not None and recovered.matched:\n                # SpotifyDetectionResult carries detection evidence, not drawable\n                # (score, x, y, w, h) coordinates. Keep preview caches box-typed.\n                setattr(self, cache_name, None)\n                continue\n'''
if c.count(old) != 1:
    raise SystemExit("watchdog recovered-cache anchor mismatch")
c = c.replace(old, new, 1)

old = '''                full = self.cached_full\n'''
new = '''                full = self._preview_box_or_none(self.cached_full)\n'''
if c.count(old) != 1:
    raise SystemExit("preview full-cache anchor mismatch")
c = c.replace(old, new, 1)

for cache_name in ("cached_dead", "cached_dc", "cached_captcha"):
    old = f'''                    (self.{cache_name},'''
    new = f'''                    (self._preview_box_or_none(self.{cache_name}),'''
    if c.count(old) != 1:
        raise SystemExit(f"preview {cache_name} anchor mismatch")
    c = c.replace(old, new, 1)

controller_path.write_bytes(c.encode("utf-8"))

ui_path = APP / "nghia_spotify_nologin.py"
u = normalized(ui_path)
if OLD_VERSION not in u:
    raise SystemExit("compact UI old version marker missing")
u = u.replace(OLD_VERSION, VERSION)
ui_path.write_bytes(u.encode("utf-8"))

(ROOT / "version.json").write_text(json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8")

for rel, expected in FINAL.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.12 final hash {rel}: {got} != {expected}")

print("V1012_PATCH_OK", FINAL)
