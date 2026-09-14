from pathlib import Path

root=Path('portable/app_payload')
strategy_src=Path('build_input/nghia_strategy_v10.py')
strategy_dst=root/'nghia_strategy_v10.py'
assert strategy_src.exists() and not strategy_dst.exists()
strategy_dst.write_text(strategy_src.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
p=root/'maple_nghia_pro.py'
t=p.read_text(encoding='utf-8')

# import
anchor='from spotify_behavior_engine import SpotifyBehaviorEngine\n'
insert=anchor+'from nghia_strategy_v10 import (\n    V10StrategyEngine, V10ProfileError, build_v10_pirate_profile,\n    is_v10_profile, legacy_neutral_map_profile,\n)\n'
assert anchor in t and 'from nghia_strategy_v10 import (' not in t
t=t.replace(anchor,insert,1)

# init
anchor='        self.behavior_engine = SpotifyBehaviorEngine(self)\n'
insert=anchor+'        self.strategy_v10 = V10StrategyEngine(self)\n'
assert anchor in t and 'self.strategy_v10 = V10StrategyEngine(self)' not in t
t=t.replace(anchor,insert,1)

# snapshot isolate
old='''        map_name = self.current_map.get().strip()\n        map_profile = self._spotify_effective_profile(map_name)\n        cfg.update({\n            "current_map": map_name,\n            "map_profile": map_profile,\n            "farm_type": str(map_profile.get("FARM_TYPE", "")).upper(),\n            "map_left_x": parse_int(map_profile.get("LEFT_X"), 0),\n            "map_left_y": parse_int(map_profile.get("LEFT_Y"), 0),\n            "map_right_x": parse_int(map_profile.get("RIGHT_X"), 0),\n            "map_right_y": parse_int(map_profile.get("RIGHT_Y"), 0),\n            "map_safe_x": parse_int(map_profile.get("SAFE_PLACE_X"), 0),\n            "map_safe_y": parse_int(map_profile.get("SAFE_PLACE_Y"), 0),\n'''
new='''        map_name = self.current_map.get().strip()\n        selected_profile = self._spotify_effective_profile(map_name)\n        v10_enabled = is_v10_profile(selected_profile)\n        map_profile = legacy_neutral_map_profile() if v10_enabled else selected_profile\n        cfg.update({\n            "current_map": map_name,\n            "map_profile": map_profile,\n            "v10_profile": dict(selected_profile) if v10_enabled else {},\n            "engine_mode": str(selected_profile.get("ENGINE_MODE", "")).upper(),\n            "farm_type": str(map_profile.get("FARM_TYPE", "")).upper(),\n            "map_left_x": parse_int(selected_profile.get("LEFT_X"), 0),\n            "map_left_y": parse_int(selected_profile.get("LEFT_Y"), 0),\n            "map_right_x": parse_int(selected_profile.get("RIGHT_X"), 0),\n            "map_right_y": parse_int(selected_profile.get("RIGHT_Y"), 0),\n            "map_safe_x": parse_int(selected_profile.get("SAFE_PLACE_X"), 0),\n            "map_safe_y": parse_int(selected_profile.get("SAFE_PLACE_Y"), 0),\n'''
assert old in t
t=t.replace(old,new,1)

# start validation gate
old='''        cfg["monster_templates"] = []\n        cfg["skills"] = []  # hard-disable legacy Nghĩa skill execution paths\n        self.runtime_cfg = dict(cfg)\n\n        if not cfg.get("spotify_attack_key"):\n'''
new='''        cfg["monster_templates"] = []\n        cfg["skills"] = []  # hard-disable legacy Nghĩa skill execution paths\n        v10_enabled = self.strategy_v10.is_runtime_cfg(cfg)\n        if v10_enabled:\n            try:\n                self.strategy_v10.validate_runtime_cfg(cfg)\n            except V10ProfileError as exc:\n                messagebox.showwarning("V10 map chưa hợp lệ", str(exc))\n                self._log(f"Không START V10: {exc}")\n                return\n        self.runtime_cfg = dict(cfg)\n\n        if not cfg.get("spotify_attack_key"):\n'''
assert old in t
t=t.replace(old,new,1)

old='''        if not self.behavior_engine.handles_profile(cfg):\n            messagebox.showwarning(\n                "Map chưa có Spotify Engine",\n                "Map hiện tại chưa có routine Spotify. V9.3 không dùng fallback skill/movement của Nghĩa."\n            )\n            self._log("Không START: map chưa có routine Spotify Engine.")\n            return\n'''
new='''        if not v10_enabled and not self.behavior_engine.handles_profile(cfg):\n            messagebox.showwarning(\n                "Map chưa có Spotify Engine",\n                "Map hiện tại chưa có routine Spotify. Legacy path không dùng fallback skill/movement của Nghĩa."\n            )\n            self._log("Không START: map chưa có routine Spotify Engine.")\n            return\n'''
assert old in t
t=t.replace(old,new,1)

# start engine branch
old='''        # V9: Nghĩa owns config/UI; the Spotify behavior engine owns farm dispatch.\n        self.behavior_engine.start(cfg)\n        self.spotify_watchdog.start(cfg)\n'''
new='''        # V10 isolation gate: legacy profiles keep the exact V9.9.8 dispatcher;\n        # opted-in maps are owned only by Strategy V10.\n        if v10_enabled:\n            self.strategy_v10.start(cfg)\n        else:\n            self.behavior_engine.start(cfg)\n        self.spotify_watchdog.start(cfg)\n'''
assert old in t
t=t.replace(old,new,1)

old='''        self._start_spotify_main_farm_worker(cfg)\n        if self.behavior_engine.handles_profile(cfg) and bool(cfg.get("spotify_runtime_parity_mode", True)):\n'''
new='''        self._start_spotify_main_farm_worker(cfg)\n        if v10_enabled:\n            r = self.strategy_v10.resolved\n            self._log(f"[V10 Strategy] ON: farm={r.farm_type} combat={r.combat_mode} tp={r.tp_mode} loot={r.loot_mode}")\n        if self.behavior_engine.handles_profile(cfg) and bool(cfg.get("spotify_runtime_parity_mode", True)):\n'''
assert old in t
t=t.replace(old,new,1)

# stop strategy first
old='''        self.spotify_all_cure_market.stop()\n        self.spotify_watchdog.stop()\n        self.behavior_engine.stop()\n'''
new='''        self.spotify_all_cure_market.stop()\n        self.spotify_watchdog.stop()\n        self.strategy_v10.stop()\n        self.behavior_engine.stop()\n'''
assert old in t
t=t.replace(old,new,1)

# map profile info branch
old='''        kind = self._spotify_profile_kind_from(name, cfg)\n        if kind == "BUNNY":\n'''
new='''        if is_v10_profile(cfg):\n            kind = "V10"\n            parts.append(\n                f"V10: {cfg.get('COMBAT_MODE')} • TP {cfg.get('TP_MODE')} • Loot {cfg.get('LOOT_MODE')}"\n            )\n        else:\n            kind = self._spotify_profile_kind_from(name, cfg)\n        if kind == "BUNNY":\n'''
assert old in t
t=t.replace(old,new,1)

old='''            self._log(f"Đã chọn hồ sơ map: {name}. Spotify farm dispatcher sẽ dùng routine {self._spotify_profile_kind_from(name, cfg)} khi START.")\n'''
new='''            if is_v10_profile(cfg):\n                self._log(f"Đã chọn hồ sơ V10: {name}. Strategy Engine chỉ kích hoạt khi START.")\n            else:\n                self._log(f"Đã chọn hồ sơ map: {name}. Spotify farm dispatcher sẽ dùng routine {self._spotify_profile_kind_from(name, cfg)} khi START.")\n'''
assert old in t
t=t.replace(old,new,1)

# bot loop safety release for V10 on supervisor exceptions and exit
old='''            except Exception as e:\n                # Fail-safe: an exception must never leave a channel skill held.\n                self.behavior_engine.release_inputs()\n'''
new='''            except Exception as e:\n                # Fail-safe: an exception must never leave a channel skill held.\n                self.strategy_v10.release_inputs()\n                self.behavior_engine.release_inputs()\n'''
assert old in t
t=t.replace(old,new,1)
old='''        self.behavior_engine.stop()\n        self.target_tracker.reset()\n'''
new='''        self.strategy_v10.stop()\n        self.behavior_engine.stop()\n        self.target_tracker.reset()\n'''
assert old in t
t=t.replace(old,new,1)

# Map Builder geometry and map types
assert 'pop.geometry("560x690")' in t
t=t.replace('pop.geometry("560x690")','pop.geometry("600x820")',1)
old='''            values=("SIMPLE", "PIRATE ROUTE"), width=20,\n'''
new='''            values=("SIMPLE", "PIRATE ROUTE", "V10 PIRATE ROUTE"), width=22,\n'''
assert old in t
t=t.replace(old,new,1)

# add V10 strategy UI after pirate values
anchor='''        for slot in pirate_slots:\n            tk.Label(\n                pirate_values, textvariable=slot_values[slot], bg=self.COLORS["panel2"],\n                fg=self.COLORS["text"], font=("Consolas", 10), anchor="w"\n            ).pack(fill="x", padx=12, pady=3)\n\n        def sync_type_ui(_event=None):\n'''
insert='''        for slot in pirate_slots:\n            tk.Label(\n                pirate_values, textvariable=slot_values[slot], bg=self.COLORS["panel2"],\n                fg=self.COLORS["text"], font=("Consolas", 10), anchor="w"\n            ).pack(fill="x", padx=12, pady=3)\n\n        strategy_frame = tk.Frame(pirate_frame, bg=self.COLORS["panel"])\n        strategy_frame.pack(fill="x", pady=(8, 0))\n        combat_mode = tk.StringVar(value="SPOTIFY_COMBO")\n        tp_mode = tk.StringVar(value="SPAM_TP_SKILL")\n        loot_mode = tk.StringVar(value="PIRATE_BOTTOM_CUSTOM")\n        strategy_specs = (\n            ("Combat", combat_mode, ("SPOTIFY_COMBO", "HOLD_SKILL_1", "SPAM_SKILL", "PIRATE_1HIT", "STAND_STILL")),\n            ("Teleport", tp_mode, ("NONE", "ROUTE_TP", "SPAM_TP_SKILL", "ADAPTIVE_Y")),\n            ("Loot", loot_mode, ("NONE", "SIMPLE", "PIRATE_BOTTOM_CUSTOM")),\n        )\n        for row, (label, var, values) in enumerate(strategy_specs):\n            tk.Label(strategy_frame, text=label, bg=self.COLORS["panel"],\n                     fg=self.COLORS["text"], font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=2)\n            ttk.Combobox(strategy_frame, textvariable=var, state="readonly",\n                         values=values, width=24).grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)\n        strategy_frame.grid_columnconfigure(1, weight=1)\n\n        def sync_type_ui(_event=None):\n'''
assert anchor in t
t=t.replace(anchor,insert,1)

# sync UI hide strategy for legacy pirate
old='''        def sync_type_ui(_event=None):\n            if map_type.get() == "PIRATE ROUTE":\n                if not pirate_frame.winfo_manager():\n                    pirate_frame.pack(fill="x")\n                status_value.set(\n                    "Pirate Route: lấy LEFT/RIGHT/SAFE và đủ 4 điểm BOTTOM LOOT"\n                )\n            else:\n                if pirate_frame.winfo_manager():\n                    pirate_frame.pack_forget()\n                status_value.set("SIMPLE: lấy LEFT, RIGHT và SAFE")\n'''
new='''        def sync_type_ui(_event=None):\n            selected_type = map_type.get()\n            if selected_type in {"PIRATE ROUTE", "V10 PIRATE ROUTE"}:\n                if not pirate_frame.winfo_manager():\n                    pirate_frame.pack(fill="x")\n                if selected_type == "V10 PIRATE ROUTE":\n                    if not strategy_frame.winfo_manager():\n                        strategy_frame.pack(fill="x", pady=(8, 0))\n                    status_value.set("V10 Pirate: lấy FARM + BOTTOM LOOT rồi chọn Combat / Teleport / Loot")\n                else:\n                    if strategy_frame.winfo_manager():\n                        strategy_frame.pack_forget()\n                    status_value.set("Pirate Route legacy: lấy LEFT/RIGHT/SAFE và đủ 4 điểm BOTTOM LOOT")\n            else:\n                if pirate_frame.winfo_manager():\n                    pirate_frame.pack_forget()\n                status_value.set("SIMPLE: lấy LEFT, RIGHT và SAFE")\n'''
assert old in t
t=t.replace(old,new,1)

# add map V10 branch
old='''            is_pirate = map_type.get() == "PIRATE ROUTE"\n            required = ["LEFT", "RIGHT", "SAFE"]\n'''
new='''            selected_type = map_type.get()\n            is_pirate = selected_type in {"PIRATE ROUTE", "V10 PIRATE ROUTE"}\n            is_v10 = selected_type == "V10 PIRATE ROUTE"\n            required = ["LEFT", "RIGHT", "SAFE"]\n'''
assert old in t
t=t.replace(old,new,1)

old='''                if is_pirate:\n                    profile = build_pirate_map_profile(\n                        captured["LEFT"], captured["RIGHT"], captured["SAFE"],\n                        captured["LOOT_LEFT"], captured["LOOT_RIGHT"],\n                        captured["LOOT_BOT_1"], captured["LOOT_BOT_2"], 0.6,\n                    )\n                else:\n'''
new='''                if is_v10:\n                    profile = build_v10_pirate_profile(\n                        captured["LEFT"], captured["RIGHT"], captured["SAFE"],\n                        captured["LOOT_LEFT"], captured["LOOT_RIGHT"],\n                        captured["LOOT_BOT_1"], captured["LOOT_BOT_2"],\n                        combat_mode.get(), tp_mode.get(), loot_mode.get(), 0.6,\n                    )\n                elif is_pirate:\n                    profile = build_pirate_map_profile(\n                        captured["LEFT"], captured["RIGHT"], captured["SAFE"],\n                        captured["LOOT_LEFT"], captured["LOOT_RIGHT"],\n                        captured["LOOT_BOT_1"], captured["LOOT_BOT_2"], 0.6,\n                    )\n                else:\n'''
assert old in t
t=t.replace(old,new,1)

old='''                if is_pirate:\n                    saved_value.set(\n                        f"Đã lưu Pirate Route {name}: FARM + 4 điểm BOTTOM LOOT"\n                    )\n                else:\n'''
new='''                if is_v10:\n                    saved_value.set(\n                        f"Đã lưu V10 {name}: {combat_mode.get()} • {tp_mode.get()} • {loot_mode.get()}"\n                    )\n                elif is_pirate:\n                    saved_value.set(\n                        f"Đã lưu Pirate Route legacy {name}: FARM + 4 điểm BOTTOM LOOT"\n                    )\n                else:\n'''
assert old in t
t=t.replace(old,new,1)

# Final isolation fixes discovered by runtime review.
old = """        if v10_enabled:\n            self.strategy_v10.start(cfg)\n        else:\n            self.behavior_engine.start(cfg)\n        self.spotify_watchdog.start(cfg)\n        self.spotify_all_cure_market.start(cfg)\n        super().start_bot()\n"""
new = """        if not v10_enabled:\n            self.behavior_engine.start(cfg)\n        self.spotify_watchdog.start(cfg)\n        self.spotify_all_cure_market.start(cfg)\n        super().start_bot()\n        if v10_enabled:\n            self.strategy_v10.start(cfg)\n"""
assert old in t
t = t.replace(old, new, 1)

old = """            except Exception as e:\n                # Fail-safe: an exception must never leave a channel skill held.\n                self.strategy_v10.release_inputs()\n                self.behavior_engine.release_inputs()\n"""
new = """            except Exception as e:\n                # Fail-safe: an exception must never leave a channel skill held.\n                if \"cfg\" in locals() and self.strategy_v10.is_runtime_cfg(cfg):\n                    self.strategy_v10.release_inputs()\n                self.behavior_engine.release_inputs()\n"""
assert old in t
t = t.replace(old, new, 1)

# Write LF deterministically
p.write_text(t,encoding='utf-8',newline='\n')

# Active UI identity
u=root/'nghia_spotify_nologin.py'
s=u.read_text(encoding='utf-8')
assert 'V9.9.8' in s and '9.9.8' in s
s=s.replace('V9.9.8','V10.0.0').replace('"9.9.8"','"10.0.0"')
u.write_text(s,encoding='utf-8',newline='\n')
print('V1000_TRANSFORM_OK')
