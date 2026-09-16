from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from v1009_release import OLD_VERSION, VERSION

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable").resolve()
APP = ROOT / "app_payload"

BASE = {
    "nghia_spotify_nologin.py": "c5e7e915856f0efdd0f027e9d6c415ac53a47fdeda775243f58e585c4c484398",
    "maple_nghia_pro.py": "1c0b98fb165278fcd983660c1551eea00d5b8e39a7ec91233e2e5fc117593265",
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
FINAL_UI_SHA256 = "347d2268e7ef850485f069d565ad5025842d3e80efa7b90ce55d32c2f93442b1"
FINAL_MAPLE_SHA256 = "bc44958038e8f94860350879b7676cd47cd532b723bcdd11167867f2f2737286"
HELPER_SHA256 = "80dfabe995f535339d404a332ea5ebde608bb1189984a6d9498206dc9c7c677c"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in BASE.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.8 base hash {rel}: {got} != {expected}")

ui_path = APP / "nghia_spotify_nologin.py"
text = ui_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
methods_anchor = '''    # ------------------------------------------------------------------\n    # Main vertical UI\n    # ------------------------------------------------------------------\n'''
methods = '''    def _on_sell_timer_toggle(self):\n        enabled = bool(self.auto_sell_timer_enabled.get())\n        runtime = getattr(self, "runtime_cfg", None)\n        if isinstance(runtime, dict):\n            runtime["auto_sell_timer_enabled"] = enabled\n        try:\n            self._log(f"[MiuMiu Timer] {'ON' if enabled else 'OFF'}")\n        except Exception:\n            pass\n\n    def _on_sell_interval_change(self, _event=None):\n        try:\n            minutes = max(0.5, float(self.sell_interval_minutes.get()))\n        except (TypeError, ValueError):\n            minutes = 30.0\n        text = str(int(minutes)) if float(minutes).is_integer() else (f"{minutes:.2f}".rstrip("0").rstrip("."))\n        self.sell_interval_minutes.set(text)\n        runtime = getattr(self, "runtime_cfg", None)\n        if isinstance(runtime, dict):\n            runtime["sell_interval_minutes"] = minutes\n        try:\n            self._log(f"[MiuMiu Timer] chu kỳ cơ sở = {text} phút")\n        except Exception:\n            pass\n\n'''
if text.count(methods_anchor) != 1:
    raise SystemExit("MiuMiu timer methods anchor mismatch")
text = text.replace(methods_anchor, methods + methods_anchor, 1)

sell_anchor = '''        ctk.CTkCheckBox(\n            box, text="Tự động bán đồ (MiuMiu)", variable=self.auto_sell,\n            text_color=self.UI["cyan"], font=self._font(10, "bold")\n        ).pack(anchor="w", padx=12, pady=(2, 6))\n\n        ctk.CTkLabel(\n'''
sell_insert = '''        ctk.CTkCheckBox(\n            box, text="Tự động bán đồ (MiuMiu)", variable=self.auto_sell,\n            text_color=self.UI["cyan"], font=self._font(10, "bold")\n        ).pack(anchor="w", padx=12, pady=(2, 6))\n\n        timer_row = ctk.CTkFrame(box, fg_color="transparent")\n        timer_row.pack(fill="x", padx=12, pady=(0, 6))\n        ctk.CTkCheckBox(\n            timer_row, text="Hẹn giờ bán MiuMiu",\n            variable=self.auto_sell_timer_enabled,\n            command=self._on_sell_timer_toggle,\n            font=self._font(9),\n        ).pack(side="left")\n        self.sell_timer_minutes_entry = ctk.CTkEntry(\n            timer_row, textvariable=self.sell_interval_minutes,\n            width=58, height=27, justify="center",\n        )\n        self.sell_timer_minutes_entry.pack(side="left", padx=(10, 4))\n        self.sell_timer_minutes_entry.bind("<Return>", self._on_sell_interval_change)\n        self.sell_timer_minutes_entry.bind("<FocusOut>", self._on_sell_interval_change)\n        ctk.CTkLabel(\n            timer_row, text="phút", text_color=self.UI["muted"],\n            font=self._font(9),\n        ).pack(side="left")\n\n        ctk.CTkLabel(\n'''
if text.count(sell_anchor) != 1:
    raise SystemExit("MiuMiu timer UI anchor mismatch")
text = text.replace(sell_anchor, sell_insert, 1)

if OLD_VERSION not in text:
    raise SystemExit(f"expected UI source to contain {OLD_VERSION}")
text = text.replace(OLD_VERSION, VERSION)
if OLD_VERSION in text:
    raise SystemExit(f"failed to replace all {OLD_VERSION} UI version strings")
ui_path.write_bytes(text.encode("utf-8"))

maple_path = APP / "maple_nghia_pro.py"
maple = maple_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
import_anchor = "from spotify_worker_supervisor import SpotifyWorkerSupervisor\n"
if maple.count(import_anchor) != 1:
    raise SystemExit("watchdog client capture import anchor mismatch")
maple = maple.replace(
    import_anchor,
    import_anchor + "from nghia_watchdog_client_capture import client_capture_region\n",
    1,
)
old_capture = '''    def _spotify_watchdog_capture_frame(self, cfg, hwnd):\n        if not hwnd:\n            return None\n        return self.capture_screen(cfg["region"], fast=cfg.get("use_fast_capture", True))\n\n'''
new_capture = '''    def _spotify_watchdog_capture_frame(self, cfg, hwnd):\n        region = client_capture_region(user32, hwnd)\n        if region is None:\n            return None\n        return self.capture_screen(region, fast=cfg.get("use_fast_capture", True))\n\n'''
if maple.count(old_capture) != 1:
    raise SystemExit("watchdog capture function anchor mismatch")
maple = maple.replace(old_capture, new_capture, 1)
maple_path.write_bytes(maple.encode("utf-8"))

helper_path = Path(__file__).resolve().with_name("nghia_watchdog_client_capture.py")
helper = helper_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
if hashlib.sha256(helper).hexdigest() != HELPER_SHA256:
    raise SystemExit("bundled watchdog client capture helper hash mismatch")
(APP / "nghia_watchdog_client_capture.py").write_bytes(helper)

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
    status["notes"] = "Nghia V10.0.9 MiuMiu Timer + CAPTCHA Client Capture"
    status["state"] = "up_to_date"
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if sha(ui_path) != FINAL_UI_SHA256:
    raise SystemExit(f"unexpected V10.0.9 final UI hash {sha(ui_path)}")
if sha(maple_path) != FINAL_MAPLE_SHA256:
    raise SystemExit(f"unexpected V10.0.9 final controller hash {sha(maple_path)}")
if sha(APP / "nghia_watchdog_client_capture.py") != HELPER_SHA256:
    raise SystemExit("unexpected V10.0.9 watchdog client capture helper hash")

print("V1009_PATCH_OK", sha(ui_path), sha(maple_path), sha(APP / "nghia_watchdog_client_capture.py"))
