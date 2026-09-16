from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from v1011_release import OLD_VERSION, VERSION

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable").resolve()
APP = ROOT / "app_payload"

BASE = {
    "nghia_spotify_nologin.py": "90b57722c81ed4def503b03764942b0d48e9de5930b4720afcee315cf34c833b",
    "maple_nghia_pro.py": "c865cbc05c56780bb13646fd5ff746e85e127ca020e5c35861323ffe43171d5a",
    "nghia_watchdog_client_capture.py": "80dfabe995f535339d404a332ea5ebde608bb1189984a6d9498206dc9c7c677c",
    "spotify_watchdog.py": "4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79",
    "spotify_pc_alarm.py": "a6c83df75b748e6a6ee398273aa8350ec5138c0f6cb64e77d6c31b1bf42ee3f4",
    "spotify_detection_parity.py": "479a6a5e9d2482fe26d040c5014e0bff61fda75426e8e690c0a173ebb002c2a1",
    "spotify_recovered_core.py": "7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048",
    "nghia_adaptive_y_ui.py": "7bc0744ffebdb645ebd6e72466aec3890b23fb5e22486be3a78ba5b6794c87ce",
    "nghia_anti_jitter.py": "25ac99c6f5c84d736d641c3c40ac33c3127f4bfd80f6bf46fec09baac899cf0e",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
    "spotify_behavior_engine.py": "8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e",
    "nghia_strategy_v10.py": "456a17da0d0fe46f69112d8e146310fb7deb66a2fe163d2fa70e497a817c6fb5",
    "spotify_main_farm_orchestrator.py": "1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68",
}

FINAL = {
    "nghia_spotify_nologin.py": "bef30874977292e4c7c408c9d69b1ccdce7654c8e571e578a5c4c53f518b6baa",
    "maple_nghia_pro.py": "f5425604caaa24f29b44ae88c62fb4276b519c6f4056c473ad2b4cd9acc4ddc5",
    "nghia_strategy_v10.py": "21b46b689771979094857b1c9da4602e45ca3c335568f3a5af306d751e5fdd99",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


for rel, expected in BASE.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.10 base hash {rel}: {got} != {expected}")

strategy_path = APP / "nghia_strategy_v10.py"
s = normalized(strategy_path)

old = '''    lx, ly = left; rx, ry = right; sx, sy = safe
    llx, lly = loot_left; lrx, lry = loot_right
    l1x, l1y = loot_bot_1; l2x, l2y = loot_bot_2
    profile = {
        "ENGINE_MODE": ENGINE_MARKER,
        "FARM_TYPE": "PIRATE_ROUTE",
        "COMBAT_MODE": _norm(combat_mode),
        "TP_MODE": _norm(tp_mode),
        "LOOT_MODE": _norm(loot_mode),
        "LEFT_X": int(round(float(lx))), "LEFT_Y": int(round(float(ly))),
        "RIGHT_X": int(round(float(rx))), "RIGHT_Y": int(round(float(ry))),
        "SAFE_PLACE_X": int(round(float(sx))), "SAFE_PLACE_Y": int(round(float(sy))),
        "LOOT_BOT_LEFT_X": int(round(float(llx))), "LOOT_BOT_LEFT_Y": int(round(float(lly))),
        "LOOT_BOT_RIGHT_X": int(round(float(lrx))), "LOOT_BOT_RIGHT_Y": int(round(float(lry))),
        "LOOT_BOT_1_X": int(round(float(l1x))), "LOOT_BOT_1_Y": int(round(float(l1y))),
        "LOOT_BOT_2_X": int(round(float(l2x))), "LOOT_BOT_2_Y": int(round(float(l2y))),
        "CHAR_MATCH_THRESHOLD": float(threshold),
'''
new = '''    lx, ly = left; rx, ry = right; sx, sy = safe
    loot_mode_norm = _norm(loot_mode)
    profile = {
        "ENGINE_MODE": ENGINE_MARKER,
        "FARM_TYPE": "PIRATE_ROUTE",
        "COMBAT_MODE": _norm(combat_mode),
        "TP_MODE": _norm(tp_mode),
        "LOOT_MODE": loot_mode_norm,
        "LEFT_X": int(round(float(lx))), "LEFT_Y": int(round(float(ly))),
        "RIGHT_X": int(round(float(rx))), "RIGHT_Y": int(round(float(ry))),
        "SAFE_PLACE_X": int(round(float(sx))), "SAFE_PLACE_Y": int(round(float(sy))),
        "CHAR_MATCH_THRESHOLD": float(threshold),
'''
if s.count(old) != 1:
    raise SystemExit("strategy simple-loot anchor mismatch")
s = s.replace(old, new, 1)

old = '''        "CUSTOM_ADAPTIVE_Y": bool(custom_adaptive_y),
    }
    resolve_v10_profile(profile)
    return profile
'''
new = '''        "CUSTOM_ADAPTIVE_Y": bool(custom_adaptive_y),
    }
    if loot_mode_norm == "PIRATE_BOTTOM_CUSTOM":
        if any(point is None for point in (loot_left, loot_right, loot_bot_1, loot_bot_2)):
            raise V10ProfileError("PIRATE_BOTTOM_CUSTOM cần đủ 4 tọa độ BOTTOM LOOT")
        llx, lly = loot_left; lrx, lry = loot_right
        l1x, l1y = loot_bot_1; l2x, l2y = loot_bot_2
        profile.update({
            "LOOT_BOT_LEFT_X": int(round(float(llx))), "LOOT_BOT_LEFT_Y": int(round(float(lly))),
            "LOOT_BOT_RIGHT_X": int(round(float(lrx))), "LOOT_BOT_RIGHT_Y": int(round(float(lry))),
            "LOOT_BOT_1_X": int(round(float(l1x))), "LOOT_BOT_1_Y": int(round(float(l1y))),
            "LOOT_BOT_2_X": int(round(float(l2x))), "LOOT_BOT_2_Y": int(round(float(l2y))),
        })
    resolve_v10_profile(profile)
    return profile
'''
if s.count(old) != 1:
    raise SystemExit("strategy conditional bottom-loot anchor mismatch")
s = s.replace(old, new, 1)
strategy_path.write_bytes(s.encode("utf-8"))

controller_path = APP / "maple_nghia_pro.py"
c = normalized(controller_path)

old = '''        pirate_buttons = tk.Frame(pirate_frame, bg=self.COLORS["panel"])
        pirate_buttons.pack(fill="x", pady=(0, 6))
        pirate_slots = ("LOOT_LEFT", "LOOT_RIGHT", "LOOT_BOT_1", "LOOT_BOT_2")
        for idx, slot in enumerate(pirate_slots):
            ttk.Button(
                pirate_buttons, text=slot_labels[slot], style="Pro.TButton",
                command=lambda s=slot: capture_slot(s)
            ).grid(row=idx // 2, column=idx % 2, sticky="ew", padx=4, pady=3)
'''
new = '''        pirate_buttons = tk.Frame(pirate_frame, bg=self.COLORS["panel"])
        pirate_buttons.pack(fill="x", pady=(0, 6))
        pirate_slots = ("LOOT_LEFT", "LOOT_RIGHT", "LOOT_BOT_1", "LOOT_BOT_2")
        pirate_button_widgets = {}
        for idx, slot in enumerate(pirate_slots):
            button = ttk.Button(
                pirate_buttons, text=slot_labels[slot], style="Pro.TButton",
                command=lambda s=slot: capture_slot(s)
            )
            button.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=4, pady=3)
            pirate_button_widgets[slot] = button
'''
if c.count(old) != 1:
    raise SystemExit("builder bottom-loot buttons anchor mismatch")
c = c.replace(old, new, 1)

old = '''        for row, (label, var, values) in enumerate(strategy_specs):
            tk.Label(strategy_frame, text=label, bg=self.COLORS["panel"],
                     fg=self.COLORS["text"], font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Combobox(strategy_frame, textvariable=var, state="readonly",
                         values=values, width=24).grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)
'''
new = '''        loot_mode_combo = None
        for row, (label, var, values) in enumerate(strategy_specs):
            tk.Label(strategy_frame, text=label, bg=self.COLORS["panel"],
                     fg=self.COLORS["text"], font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            combo = ttk.Combobox(strategy_frame, textvariable=var, state="readonly",
                                 values=values, width=24)
            combo.grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)
            if label == "Loot":
                loot_mode_combo = combo
'''
if c.count(old) != 1:
    raise SystemExit("builder loot combobox anchor mismatch")
c = c.replace(old, new, 1)

old = '''        def sync_type_ui(_event=None):
            selected_type = map_type.get()
            if selected_type in {"PIRATE ROUTE", "V10 PIRATE ROUTE"}:
                if not pirate_frame.winfo_manager():
                    pirate_frame.pack(fill="x")
                if selected_type == "V10 PIRATE ROUTE":
                    if not strategy_frame.winfo_manager():
                        strategy_frame.pack(fill="x", pady=(8, 0))
                    status_value.set("V10 Pirate: lấy FARM + BOTTOM LOOT rồi chọn Combat / Teleport / Loot")
                else:
                    if strategy_frame.winfo_manager():
                        strategy_frame.pack_forget()
                    status_value.set("Pirate Route legacy: lấy LEFT/RIGHT/SAFE và đủ 4 điểm BOTTOM LOOT")
            else:
                if pirate_frame.winfo_manager():
                    pirate_frame.pack_forget()
                status_value.set("SIMPLE: lấy LEFT, RIGHT và SAFE")

        type_combo.bind("<<ComboboxSelected>>", sync_type_ui)
        sync_type_ui()
'''
new = '''        def sync_loot_ui(_event=None):
            selected_type = map_type.get()
            needs_bottom_loot = (
                selected_type == "PIRATE ROUTE"
                or (
                    selected_type == "V10 PIRATE ROUTE"
                    and loot_mode.get() == "PIRATE_BOTTOM_CUSTOM"
                )
            )
            state = "normal" if needs_bottom_loot else "disabled"
            for slot, button in pirate_button_widgets.items():
                button.configure(state=state)
                if captured[slot] is None:
                    if selected_type == "V10 PIRATE ROUTE" and not needs_bottom_loot:
                        slot_values[slot].set(f"{slot_labels[slot]}: không cần với Loot={loot_mode.get()}")
                    else:
                        slot_values[slot].set(f"{slot_labels[slot]}: chưa lấy")
            if selected_type == "V10 PIRATE ROUTE" and not needs_bottom_loot:
                status_value.set(
                    f"V10 {loot_mode.get()}: chỉ cần LEFT/RIGHT/SAFE; 4 điểm BOTTOM LOOT không bắt buộc"
                )

        def sync_type_ui(_event=None):
            selected_type = map_type.get()
            if selected_type in {"PIRATE ROUTE", "V10 PIRATE ROUTE"}:
                if not pirate_frame.winfo_manager():
                    pirate_frame.pack(fill="x")
                if selected_type == "V10 PIRATE ROUTE":
                    if not strategy_frame.winfo_manager():
                        strategy_frame.pack(fill="x", pady=(8, 0))
                    status_value.set("V10 Pirate: chọn Combat / Teleport / Loot; BOTTOM LOOT chỉ cần khi dùng PIRATE_BOTTOM_CUSTOM")
                else:
                    if strategy_frame.winfo_manager():
                        strategy_frame.pack_forget()
                    status_value.set("Pirate Route legacy: lấy LEFT/RIGHT/SAFE và đủ 4 điểm BOTTOM LOOT")
            else:
                if pirate_frame.winfo_manager():
                    pirate_frame.pack_forget()
                status_value.set("SIMPLE: lấy LEFT, RIGHT và SAFE")
            sync_loot_ui()

        type_combo.bind("<<ComboboxSelected>>", sync_type_ui)
        if loot_mode_combo is not None:
            loot_mode_combo.bind("<<ComboboxSelected>>", sync_loot_ui)
        sync_type_ui()
'''
if c.count(old) != 1:
    raise SystemExit("builder type sync anchor mismatch")
c = c.replace(old, new, 1)

old = '''            required = ["LEFT", "RIGHT", "SAFE"]
            if is_pirate:
                required.extend(["LOOT_LEFT", "LOOT_RIGHT", "LOOT_BOT_1", "LOOT_BOT_2"])
'''
new = '''            required = ["LEFT", "RIGHT", "SAFE"]
            needs_bottom_loot = is_pirate and (not is_v10 or loot_mode.get() == "PIRATE_BOTTOM_CUSTOM")
            if needs_bottom_loot:
                required.extend(["LOOT_LEFT", "LOOT_RIGHT", "LOOT_BOT_1", "LOOT_BOT_2"])
'''
if c.count(old) != 1:
    raise SystemExit("builder required coordinate anchor mismatch")
c = c.replace(old, new, 1)

old = '''                if is_v10:
                    profile = build_v10_pirate_profile(
                        captured["LEFT"], captured["RIGHT"], captured["SAFE"],
                        captured["LOOT_LEFT"], captured["LOOT_RIGHT"],
                        captured["LOOT_BOT_1"], captured["LOOT_BOT_2"],
                        combat_mode.get(), tp_mode.get(), loot_mode.get(), 0.6,
'''
new = '''                if is_v10:
                    loot_left = captured["LOOT_LEFT"] if needs_bottom_loot else None
                    loot_right = captured["LOOT_RIGHT"] if needs_bottom_loot else None
                    loot_bot_1 = captured["LOOT_BOT_1"] if needs_bottom_loot else None
                    loot_bot_2 = captured["LOOT_BOT_2"] if needs_bottom_loot else None
                    profile = build_v10_pirate_profile(
                        captured["LEFT"], captured["RIGHT"], captured["SAFE"],
                        loot_left, loot_right, loot_bot_1, loot_bot_2,
                        combat_mode.get(), tp_mode.get(), loot_mode.get(), 0.6,
'''
if c.count(old) != 1:
    raise SystemExit("builder profile construction anchor mismatch")
c = c.replace(old, new, 1)
controller_path.write_bytes(c.encode("utf-8"))

ui_path = APP / "nghia_spotify_nologin.py"
u = normalized(ui_path)
if OLD_VERSION not in u:
    raise SystemExit(f"expected UI to contain {OLD_VERSION}")
u = u.replace(OLD_VERSION, VERSION)
if OLD_VERSION in u:
    raise SystemExit("V10.0.10 version token remained in compact UI")
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
    status["notes"] = "Nghia V10.0.11 Simple Loot Optional Coordinates"
    status["state"] = "up_to_date"
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

for rel, expected in FINAL.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"unexpected V10.0.11 final hash {rel}: {got} != {expected}")

for rel in (
    "maps.json",
    "spotify_recovered_core.py",
    "spotify_behavior_engine.py",
    "spotify_watchdog.py",
    "spotify_pc_alarm.py",
    "spotify_detection_parity.py",
    "nghia_watchdog_client_capture.py",
    "nghia_anti_jitter.py",
    "nghia_adaptive_y_ui.py",
    "spotify_main_farm_orchestrator.py",
):
    expected = BASE[rel]
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f"protected file changed {rel}: {got} != {expected}")

print("V1011_PATCH_OK", sha(strategy_path), sha(controller_path), sha(ui_path))
