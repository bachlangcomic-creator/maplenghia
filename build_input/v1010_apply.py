from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from v1010_release import OLD_VERSION, VERSION

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable").resolve()
APP = ROOT / "app_payload"

BASE = {
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


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


for rel, expected in BASE.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.9 base hash {rel}: {got} != {expected}")

# ---------------------------------------------------------------------------
# Strategy V10: four opt-in Custom Map parity features. OFF remains true bypass.
# ---------------------------------------------------------------------------
strategy_path = APP / "nghia_strategy_v10.py"
s = normalized(strategy_path)

old = '''def build_v10_pirate_profile(\n    left, right, safe, loot_left, loot_right, loot_bot_1, loot_bot_2,\n    combat_mode="SPOTIFY_COMBO", tp_mode="SPAM_TP_SKILL",\n    loot_mode="PIRATE_BOTTOM_CUSTOM", threshold=0.6,\n):\n'''
new = '''def build_v10_pirate_profile(\n    left, right, safe, loot_left, loot_right, loot_bot_1, loot_bot_2,\n    combat_mode="SPOTIFY_COMBO", tp_mode="SPAM_TP_SKILL",\n    loot_mode="PIRATE_BOTTOM_CUSTOM", threshold=0.6,\n    *, custom_simple_human=False, custom_fall_recovery=False,\n    custom_loot_jitter=False, custom_adaptive_y=False,\n):\n'''
if s.count(old) != 1:
    raise SystemExit("strategy builder signature anchor mismatch")
s = s.replace(old, new, 1)

old = '''        "CHAR_MATCH_THRESHOLD": float(threshold),\n    }\n'''
new = '''        "CHAR_MATCH_THRESHOLD": float(threshold),\n        "CUSTOM_SIMPLE_HUMAN": bool(custom_simple_human),\n        "CUSTOM_FALL_RECOVERY": bool(custom_fall_recovery),\n        "CUSTOM_LOOT_JITTER": bool(custom_loot_jitter),\n        "CUSTOM_ADAPTIVE_Y": bool(custom_adaptive_y),\n    }\n'''
if s.count(old) != 1:
    raise SystemExit("strategy profile flag anchor mismatch")
s = s.replace(old, new, 1)

old = '''    ADAPTIVE_Y_HARD_BAND = 12.0\n    ADAPTIVE_Y_ACTION_INTERVAL = 0.40\n'''
new = '''    ADAPTIVE_Y_HARD_BAND = 12.0\n    ADAPTIVE_Y_ACTION_INTERVAL = 0.40\n    HUMAN_REST_PROBABILITY = 0.02\n    HUMAN_JUMP_CUMULATIVE = 0.08\n    FALL_RECOVERY_BAND = 12.0\n    FALL_RECOVERY_CONFIRM = 2.50\n    FALL_RECOVERY_COOLDOWN = 0.80\n'''
if s.count(old) != 1:
    raise SystemExit("strategy constants anchor mismatch")
s = s.replace(old, new, 1)

old = '''        self.next_adaptive_action_at = 0.0\n        self.adaptive_y_anchor: Optional[float] = None\n        self.held_attack_key: Optional[str] = None\n'''
new = '''        self.next_adaptive_action_at = 0.0\n        self.adaptive_y_anchor: Optional[float] = None\n        self.human_pause_until = 0.0\n        self.fall_off_since: Optional[float] = None\n        self.next_fall_recovery_at = 0.0\n        self.held_attack_key: Optional[str] = None\n'''
if s.count(old) != 1:
    raise SystemExit("strategy init state anchor mismatch")
s = s.replace(old, new, 1)

old = '''        self.next_adaptive_action_at = now\n        self.adaptive_y_anchor = None\n        self.last_position = None\n'''
new = '''        self.next_adaptive_action_at = now\n        self.adaptive_y_anchor = None\n        self.human_pause_until = 0.0\n        self.fall_off_since = None\n        self.next_fall_recovery_at = now\n        self.last_position = None\n'''
if s.count(old) != 1:
    raise SystemExit("strategy start reset anchor mismatch")
s = s.replace(old, new, 1)

old = '''    def _loot_delay(self, cfg: Mapping[str, Any]) -> float:\n        try:\n            base = float(cfg.get("loot_time", cfg.get("spotify_loot_time", 90.0)) or 90.0)\n        except Exception:\n            base = 90.0\n        return max(self.SIMPLE_LOOT_MIN_INTERVAL, base)\n\n'''
new = '''    def _custom_flag(self, name: str) -> bool:\n        value = self.profile.get(name, False)\n        if isinstance(value, str):\n            return value.strip().lower() in {"1", "true", "yes", "on"}\n        return bool(value)\n\n    def _loot_delay(self, cfg: Mapping[str, Any]) -> float:\n        try:\n            base = float(cfg.get("loot_time", cfg.get("spotify_loot_time", 90.0)) or 90.0)\n        except Exception:\n            base = 90.0\n        if self._custom_flag("CUSTOM_LOOT_JITTER"):\n            base *= random.uniform(0.9, 1.1)\n        return max(self.SIMPLE_LOOT_MIN_INTERVAL, base)\n\n'''
if s.count(old) != 1:
    raise SystemExit("strategy loot delay anchor mismatch")
s = s.replace(old, new, 1)

old = '''    def tick(self, cfg: Mapping[str, Any], map_pos, now: float) -> bool:\n        resolved = self.resolved\n        if not self.running or resolved is None:\n            return False\n        if bool(cfg.get("pause_on_focus_loss", True)):\n            checker = getattr(self.host, "_game_has_focus", None)\n            if callable(checker) and not checker(cfg):\n                self.release_inputs()\n                return False\n        if map_pos is None:\n            self.release_inputs()\n            return False\n        if self.loot_state != "FARM":\n            return self._custom_loot_step(cfg, map_pos, now)\n        if self._maybe_begin_loot(cfg, now):\n            return True\n        edge_hit = self._farm_route_step(cfg, map_pos, now)\n        if resolved.tp_mode == "ADAPTIVE_Y":\n            self._adaptive_y_step(cfg, map_pos, now)\n        elif resolved.tp_mode in {"ROUTE_TP", "SPAM_TP_SKILL"}:\n            self._teleport_step(cfg, map_pos, now)\n        self._combat_step(cfg, map_pos, now, edge_hit=edge_hit)\n        return True\n\n'''
new = '''    def tick(self, cfg: Mapping[str, Any], map_pos, now: float) -> bool:\n        resolved = self.resolved\n        if not self.running or resolved is None:\n            return False\n        if bool(cfg.get("pause_on_focus_loss", True)):\n            checker = getattr(self.host, "_game_has_focus", None)\n            if callable(checker) and not checker(cfg):\n                self.release_inputs()\n                return False\n        if map_pos is None:\n            self.release_inputs()\n            return False\n        if self.loot_state != "FARM":\n            return self._custom_loot_step(cfg, map_pos, now)\n        if self._maybe_begin_loot(cfg, now):\n            return True\n        if now < self.human_pause_until:\n            self._release_attack_hold()\n            self.host.release_move()\n            return True\n        edge_hit = self._farm_route_step(cfg, map_pos, now)\n        if edge_hit and self._maybe_human_behavior(cfg, now):\n            return True\n        if resolved.tp_mode == "ADAPTIVE_Y" or self._custom_flag("CUSTOM_ADAPTIVE_Y"):\n            self._adaptive_y_step(cfg, map_pos, now)\n        elif resolved.tp_mode in {"ROUTE_TP", "SPAM_TP_SKILL"}:\n            self._teleport_step(cfg, map_pos, now)\n        self._fall_recovery_step(cfg, map_pos, now)\n        self._combat_step(cfg, map_pos, now, edge_hit=edge_hit)\n        return True\n\n    def _maybe_human_behavior(self, cfg, now: float) -> bool:\n        if not self._custom_flag("CUSTOM_SIMPLE_HUMAN"):\n            return False\n        roll = random.random()\n        if roll < self.HUMAN_REST_PROBABILITY:\n            self._release_attack_hold()\n            self.host.release_move()\n            self.human_pause_until = now + random.uniform(3.0, 5.0)\n            return True\n        if roll < self.HUMAN_JUMP_CUMULATIVE:\n            key = str(cfg.get("jump_key") or "").strip()\n            if not key:\n                return False\n            return bool(self.host.behavior_engine.core._spotify_input_semantic(\n                cfg, "JUMP", key, hold_ms=random.randint(150, 300)\n            ))\n        return False\n\n'''
if s.count(old) != 1:
    raise SystemExit("strategy tick anchor mismatch")
s = s.replace(old, new, 1)

old = '''    def _adaptive_y_step(self, cfg, map_pos, now: float) -> bool:\n        if now < self.next_adaptive_action_at:\n            return False\n        py = float(map_pos[1])\n        if self.adaptive_y_anchor is None:\n            self.adaptive_y_anchor = py\n            return False\n        delta = py - self.adaptive_y_anchor\n        if abs(delta) <= self.ADAPTIVE_Y_HARD_BAND:\n            return False\n        core = self.host.behavior_engine.core\n        ok = False\n        if delta < 0:\n            if cfg.get("tele_enabled") and cfg.get("tele_key"):\n                ok = bool(core._spotify_flash_down(cfg))\n            if not ok and cfg.get("jump_key"):\n                ok = bool(core._spotify_jump_down_reconstructed(cfg))\n        else:\n            ok = bool(core._spotify_jump_up(cfg))\n        self.next_adaptive_action_at = time.monotonic() + self.ADAPTIVE_Y_ACTION_INTERVAL\n        return ok\n\n'''
new = '''    def _vertical_recovery_action(self, cfg, delta: float) -> bool:\n        core = self.host.behavior_engine.core\n        ok = False\n        if delta < 0:\n            if cfg.get("tele_enabled") and cfg.get("tele_key"):\n                ok = bool(core._spotify_flash_down(cfg))\n            if not ok and cfg.get("jump_key"):\n                ok = bool(core._spotify_jump_down_reconstructed(cfg))\n        else:\n            ok = bool(core._spotify_jump_up(cfg))\n        return ok\n\n    def _adaptive_y_step(self, cfg, map_pos, now: float) -> bool:\n        if now < self.next_adaptive_action_at:\n            return False\n        py = float(map_pos[1])\n        if self.adaptive_y_anchor is None:\n            self.adaptive_y_anchor = py\n            return False\n        delta = py - self.adaptive_y_anchor\n        if abs(delta) <= self.ADAPTIVE_Y_HARD_BAND:\n            return False\n        ok = self._vertical_recovery_action(cfg, delta)\n        self.next_adaptive_action_at = time.monotonic() + self.ADAPTIVE_Y_ACTION_INTERVAL\n        return ok\n\n    def _fall_recovery_step(self, cfg, map_pos, now: float) -> bool:\n        if not self._custom_flag("CUSTOM_FALL_RECOVERY"):\n            self.fall_off_since = None\n            return False\n        resolved = self.resolved\n        if resolved is None:\n            return False\n        if self._custom_flag("CUSTOM_ADAPTIVE_Y") and self.adaptive_y_anchor is not None:\n            lane_y = float(self.adaptive_y_anchor)\n        else:\n            lane_y = (float(resolved.left[1]) + float(resolved.right[1])) / 2.0\n        delta = float(map_pos[1]) - lane_y\n        if abs(delta) <= self.FALL_RECOVERY_BAND:\n            self.fall_off_since = None\n            return False\n        if self.fall_off_since is None:\n            self.fall_off_since = now\n            return False\n        if now - self.fall_off_since < self.FALL_RECOVERY_CONFIRM:\n            return False\n        if now < self.next_fall_recovery_at:\n            return False\n        ok = self._vertical_recovery_action(cfg, delta)\n        self.next_fall_recovery_at = now + self.FALL_RECOVERY_COOLDOWN\n        self.fall_off_since = now\n        return ok\n\n'''
if s.count(old) != 1:
    raise SystemExit("strategy adaptive/fall recovery anchor mismatch")
s = s.replace(old, new, 1)
strategy_path.write_bytes(s.encode("utf-8"))

# ---------------------------------------------------------------------------
# Map Builder UI: four V10 Custom Map toggles, OFF by default.
# ---------------------------------------------------------------------------
controller_path = APP / "maple_nghia_pro.py"
c = normalized(controller_path)
if c.count('pop.geometry("600x820")') != 1:
    raise SystemExit("custom map builder geometry anchor mismatch")
c = c.replace('pop.geometry("600x820")', 'pop.geometry("620x930")', 1)

old = '''        combat_mode = tk.StringVar(value="SPOTIFY_COMBO")\n        tp_mode = tk.StringVar(value="SPAM_TP_SKILL")\n        loot_mode = tk.StringVar(value="PIRATE_BOTTOM_CUSTOM")\n        strategy_specs = (\n'''
new = '''        combat_mode = tk.StringVar(value="SPOTIFY_COMBO")\n        tp_mode = tk.StringVar(value="SPAM_TP_SKILL")\n        loot_mode = tk.StringVar(value="PIRATE_BOTTOM_CUSTOM")\n        custom_simple_human = tk.BooleanVar(value=False)\n        custom_fall_recovery = tk.BooleanVar(value=False)\n        custom_loot_jitter = tk.BooleanVar(value=False)\n        custom_adaptive_y = tk.BooleanVar(value=False)\n        strategy_specs = (\n'''
if c.count(old) != 1:
    raise SystemExit("custom map option variable anchor mismatch")
c = c.replace(old, new, 1)

old = '''        strategy_frame.grid_columnconfigure(1, weight=1)\n\n        def sync_type_ui(_event=None):\n'''
new = '''        strategy_frame.grid_columnconfigure(1, weight=1)\n        custom_opts = tk.Frame(strategy_frame, bg=self.COLORS["panel"])\n        custom_opts.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))\n        custom_option_specs = (\n            ("SIMPLE Human Behavior", custom_simple_human),\n            ("B1/B3 Fall Recovery", custom_fall_recovery),\n            ("Loot Jitter kiểu Spotify", custom_loot_jitter),\n            ("Adaptive Y cho Custom Map", custom_adaptive_y),\n        )\n        for row, (label, var) in enumerate(custom_option_specs):\n            ttk.Checkbutton(custom_opts, text=label, variable=var).grid(\n                row=row, column=0, sticky="w", pady=2\n            )\n\n        def sync_type_ui(_event=None):\n'''
if c.count(old) != 1:
    raise SystemExit("custom map option UI anchor mismatch")
c = c.replace(old, new, 1)

old = '''                    profile = build_v10_pirate_profile(\n                        captured["LEFT"], captured["RIGHT"], captured["SAFE"],\n                        captured["LOOT_LEFT"], captured["LOOT_RIGHT"],\n                        captured["LOOT_BOT_1"], captured["LOOT_BOT_2"],\n                        combat_mode.get(), tp_mode.get(), loot_mode.get(), 0.6,\n                    )\n'''
new = '''                    profile = build_v10_pirate_profile(\n                        captured["LEFT"], captured["RIGHT"], captured["SAFE"],\n                        captured["LOOT_LEFT"], captured["LOOT_RIGHT"],\n                        captured["LOOT_BOT_1"], captured["LOOT_BOT_2"],\n                        combat_mode.get(), tp_mode.get(), loot_mode.get(), 0.6,\n                        custom_simple_human=custom_simple_human.get(),\n                        custom_fall_recovery=custom_fall_recovery.get(),\n                        custom_loot_jitter=custom_loot_jitter.get(),\n                        custom_adaptive_y=custom_adaptive_y.get(),\n                    )\n'''
if c.count(old) != 1:
    raise SystemExit("custom map profile persistence anchor mismatch")
c = c.replace(old, new, 1)
controller_path.write_bytes(c.encode("utf-8"))

# Compact UI version bump only; V10.0.9 MiuMiu timer remains byte-for-byte otherwise.
ui_path = APP / "nghia_spotify_nologin.py"
u = normalized(ui_path)
if OLD_VERSION not in u:
    raise SystemExit(f"expected UI to contain {OLD_VERSION}")
u = u.replace(OLD_VERSION, VERSION)
if OLD_VERSION in u:
    raise SystemExit("V10.0.9 version token remained in compact UI")
ui_path.write_bytes(u.encode("utf-8"))

version_path = ROOT / "version.json"
version_obj = json.loads(version_path.read_text(encoding="utf-8"))
if version_obj.get("version") != OLD_VERSION:
    raise SystemExit(f"unexpected base version.json {version_obj!r}")
version_obj["version"] = VERSION
version_path.write_text(json.dumps(version_obj, indent=2) + "\n", encoding="utf-8")

status_path = ROOT / "user_data" / "update_status.json"
if status_path.is_file():
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["latest_version"] = VERSION
    status["local_version"] = VERSION
    status["notes"] = "Nghia V10.0.10 Custom Map Parity"
    status["state"] = "up_to_date"
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Guard protected parts that this release must not alter.
for rel in (
    "maps.json",
    "spotify_recovered_core.py",
    "spotify_behavior_engine.py",
    "spotify_watchdog.py",
    "spotify_pc_alarm.py",
    "nghia_watchdog_client_capture.py",
    "nghia_anti_jitter.py",
    "nghia_adaptive_y_ui.py",
    "spotify_main_farm_orchestrator.py",
):
    expected = BASE[rel]
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"protected file changed {rel}: {got} != {expected}")

print("V1010_PATCH_OK", sha(strategy_path), sha(controller_path), sha(ui_path))
