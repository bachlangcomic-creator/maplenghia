from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable").resolve()
APP = ROOT / "app_payload"
VERSION = "10.0.14"
OLD_VERSION = "10.0.13"

BASE = {
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

FINAL = {
    "nghia_spotify_nologin.py": "5892f9a3977ea7ee2e0416fdeaf8021e014f3d2912f498f4ceaa843a5668aab2",
    "maple_nghia_pro.py": "a24fdae1dbc69bb380ec0e3cf8cbc19fb2d34a799a6c782432844e36cdc0c408",
    "nghia_strategy_v10.py": "e1e256a4abef2d412aa56e481c753fc4debc6485ffed3e7d410a0d707032e1b2",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


for rel, expected in BASE.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.13 base hash {rel}: {got} != {expected}")

controller_path = APP / "maple_nghia_pro.py"
c = normalized(controller_path)
old = '''        condition_due = (not cfg.get("sell_only_when_full")) or self.spotify_full_bag_event.is_set()\n        cooldown_ok = (now - self.last_sell_time) * 1000 >= cfg["sell_cooldown"]\n        sell_requested = bool(\n            cfg.get("auto_sell") and cooldown_ok and\n            (self.spotify_sell_timer_event.is_set() or condition_due)\n        )\n'''
new = '''        timer_mode = bool(cfg.get("auto_sell_timer_enabled"))\n        timer_due = self.spotify_sell_timer_event.is_set()\n        full_bag_due = self.spotify_full_bag_event.is_set()\n        trigger_due = timer_due if timer_mode else full_bag_due\n        cooldown_ok = (now - self.last_sell_time) * 1000 >= cfg["sell_cooldown"]\n        sell_requested = bool(cfg.get("auto_sell") and cooldown_ok and trigger_due)\n'''
if c.count(old) != 1:
    raise SystemExit("V10.0.14 SELL_SAFE trigger anchor mismatch")
c = c.replace(old, new, 1)
controller_path.write_bytes(c.encode("utf-8"))

ui_path = APP / "nghia_spotify_nologin.py"
u = normalized(ui_path)
anchor = '''    def _on_sell_timer_toggle(self):\n'''
helper = '''    def _on_auto_sell_toggle(self):\n        enabled = bool(self.auto_sell.get())\n        runtime = getattr(self, "runtime_cfg", None)\n        if isinstance(runtime, dict):\n            runtime["auto_sell"] = enabled\n        for event_name in ("spotify_full_bag_event", "spotify_sell_timer_event"):\n            event = getattr(self, event_name, None)\n            if event is not None and callable(getattr(event, "clear", None)):\n                event.clear()\n        watchdog = getattr(self, "spotify_watchdog", None)\n        reset_schedule = getattr(watchdog, "notify_sell_completed", None)\n        if callable(reset_schedule):\n            reset_schedule()\n        try:\n            self._log(f"[MiuMiu] Auto Sell {'ON' if enabled else 'OFF'}; reset trigger cũ")\n        except Exception:\n            pass\n\n'''
if u.count(anchor) != 1:
    raise SystemExit("V10.0.14 compact UI handler anchor mismatch")
u = u.replace(anchor, helper + anchor, 1)

old_box = '''        ctk.CTkCheckBox(\n            box, text="Tự động bán đồ (MiuMiu)", variable=self.auto_sell,\n            text_color=self.UI["cyan"], font=self._font(10, "bold")\n        ).pack(anchor="w", padx=12, pady=(2, 6))\n'''
new_box = '''        ctk.CTkCheckBox(\n            box, text="Tự động bán đồ (MiuMiu)", variable=self.auto_sell,\n            command=self._on_auto_sell_toggle,\n            text_color=self.UI["cyan"], font=self._font(10, "bold")\n        ).pack(anchor="w", padx=12, pady=(2, 6))\n'''
if u.count(old_box) != 1:
    raise SystemExit("V10.0.14 Auto Sell checkbox anchor mismatch")
u = u.replace(old_box, new_box, 1)

if "V10.0.13" not in u and "10.0.13" not in u:
    raise SystemExit("V10.0.13 UI version marker missing")
u = u.replace("V10.0.13", "V10.0.14").replace("10.0.13", "10.0.14")
if "10.0.13" in u:
    raise SystemExit("failed to replace all V10.0.13 UI version markers")
ui_path.write_bytes(u.encode("utf-8"))

(ROOT / "version.json").write_text(json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8")

for rel, expected in FINAL.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.14 final hash {rel}: {got} != {expected}")

print("V1014_PATCH_OK", FINAL)
