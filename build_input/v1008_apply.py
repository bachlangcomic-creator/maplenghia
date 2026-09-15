from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from v1008_release import OLD_VERSION, VERSION

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
BASE_UI_SHA256 = "ad8a816b0ca2367ee7969099a79120934fab28e7804cc7739f7dc87cfbf673df"
FINAL_UI_SHA256 = "c5e7e915856f0efdd0f027e9d6c415ac53a47fdeda775243f58e585c4c484398"
HELPER_SHA256 = "7bc0744ffebdb645ebd6e72466aec3890b23fb5e22486be3a78ba5b6794c87ce"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for rel, expected in PROTECTED.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"protected V10.0.7 file changed before V10.0.8 patch: {rel} {got}")

ui_path = APP / "nghia_spotify_nologin.py"
ui_before = ui_path.read_bytes()
if hashlib.sha256(ui_before).hexdigest() != BASE_UI_SHA256:
    raise SystemExit("unexpected V10.0.7 UI source hash")
text = ui_before.decode("utf-8")

import_anchor = "from maple_nghia_pro import MapleNghiaPro, DIRECT_INPUT_AVAILABLE\n"
if text.count(import_anchor) != 1:
    raise SystemExit("Adaptive Y helper import anchor mismatch")
text = text.replace(
    import_anchor,
    import_anchor + "from nghia_adaptive_y_ui import adaptive_y_ui_state\n",
    1,
)

checkbox_anchor = '''        ctk.CTkCheckBox(\n            box,\n            text="Anti-Jitter / Hysteresis • OFF = V10.0.7 gốc",\n'''
checkbox_insert = '''        self.adaptive_y_checkbox = ctk.CTkCheckBox(\n            box,\n            text="Adaptive Y • không áp dụng cho map này",\n            command=self._on_adaptive_y_map_toggle,\n            text_color=c["text"],\n            fg_color=c["cyan"],\n            hover_color=c["cyan_hover"],\n            border_color=c["line_bright"],\n            font=self._font(10, "bold"),\n        )\n        self.adaptive_y_checkbox.pack(anchor="w", padx=12, pady=(0, 7))\n        self._sync_adaptive_y_map_toggle()\n\n        ctk.CTkCheckBox(\n            box,\n            text="Anti-Jitter / Hysteresis • OFF = V10.0.7 gốc",\n'''
if text.count(checkbox_anchor) != 1:
    raise SystemExit("Adaptive Y checkbox anchor mismatch")
text = text.replace(checkbox_anchor, checkbox_insert, 1)

init_anchor = '''        super().__init__()\n        self.title("Nghia Edition V10.0.7 • Nghĩa UI + Spotify Recovered Core")\n'''
init_replace = '''        super().__init__()\n        self._sync_adaptive_y_map_toggle()\n        self.title("Nghia Edition V10.0.7 • Nghĩa UI + Spotify Recovered Core")\n'''
if text.count(init_anchor) != 1:
    raise SystemExit("Adaptive Y post-config sync anchor mismatch")
text = text.replace(init_anchor, init_replace, 1)

method_anchor = '''    def _on_map_change(self, _value=None):\n        self._apply_map_profile(first=False)\n        self._refresh_quick_map_buttons()\n\n'''
method_replace = '''    def _adaptive_y_state_for_current_map(self):\n        return adaptive_y_ui_state(\n            self.current_map.get(),\n            c2_enabled=bool(self.c2_adaptive_y_enabled.get()),\n            b3_enabled=bool(self.b3_adaptive_y_enabled.get()),\n        )\n\n    def _sync_adaptive_y_map_toggle(self):\n        checkbox = getattr(self, "adaptive_y_checkbox", None)\n        if checkbox is None:\n            return\n        state = self._adaptive_y_state_for_current_map()\n        checkbox.configure(\n            text=state.label,\n            state="normal" if state.enabled else "disabled",\n        )\n        if state.checked:\n            checkbox.select()\n        else:\n            checkbox.deselect()\n\n    def _on_adaptive_y_map_toggle(self):\n        state = self._adaptive_y_state_for_current_map()\n        if not state.enabled or not state.config_key:\n            self._sync_adaptive_y_map_toggle()\n            return\n        enabled = bool(self.adaptive_y_checkbox.get())\n        target_var = (\n            self.c2_adaptive_y_enabled\n            if state.config_key == "c2_adaptive_y_enabled"\n            else self.b3_adaptive_y_enabled\n        )\n        target_var.set(enabled)\n        if isinstance(getattr(self, "runtime_cfg", None), dict):\n            self.runtime_cfg[state.config_key] = enabled\n        try:\n            self.behavior_engine.core._spotify_reset_c2_adaptive_y_state(clear_anchor=True)\n        except Exception:\n            self.spotify_simple_adaptive_y = None\n        self._apply_map_profile(first=False)\n        self._sync_adaptive_y_map_toggle()\n        self._log(\n            f"[Adaptive Y] {str(self.current_map.get()).strip().upper()} "\n            f"{'ON' if enabled else 'OFF'}"\n        )\n\n    def _on_map_change(self, _value=None):\n        self._apply_map_profile(first=False)\n        self._refresh_quick_map_buttons()\n        self._sync_adaptive_y_map_toggle()\n\n'''
if text.count(method_anchor) != 1:
    raise SystemExit("Adaptive Y map change anchor mismatch")
text = text.replace(method_anchor, method_replace, 1)

if OLD_VERSION not in text:
    raise SystemExit(f"expected UI source to contain {OLD_VERSION}")
text = text.replace(OLD_VERSION, VERSION)
if OLD_VERSION in text:
    raise SystemExit(f"failed to replace all {OLD_VERSION} UI version strings")
ui_path.write_bytes(text.encode("utf-8"))

helper_path = Path(__file__).resolve().with_name("nghia_adaptive_y_ui.py")
helper_src = helper_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
if hashlib.sha256(helper_src).hexdigest() != HELPER_SHA256:
    raise SystemExit("bundled Adaptive Y helper source hash mismatch")
(APP / "nghia_adaptive_y_ui.py").write_bytes(helper_src)

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
    status["notes"] = "Nghia V10.0.8 Map-Aware Adaptive Y Toggle"
    status["state"] = "up_to_date"
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if sha(ui_path) != FINAL_UI_SHA256:
    raise SystemExit(f"unexpected V10.0.8 final UI hash {sha(ui_path)}")
if sha(APP / "nghia_adaptive_y_ui.py") != HELPER_SHA256:
    raise SystemExit("unexpected V10.0.8 Adaptive Y helper hash")

print("V1008_ADAPTIVE_Y_MAP_AWARE_PATCH_OK", sha(ui_path), sha(APP / "nghia_adaptive_y_ui.py"))