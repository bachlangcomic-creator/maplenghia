from __future__ import annotations

from pathlib import Path
import sys

MARKER = "V10.0.17_SAFE_ENTRY_RETURN"


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def _replace_count(text: str, old: str, new: str, expected: int, label: str) -> str:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} anchors, found {count}")
    return text.replace(old, new)


def _patch_controller(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return
    if "SAFE_ENTRY_X" in text or "FARM_RETURN" in text:
        raise SystemExit("V10.0.17 must start from the exact V10.0.15 source without SAFE ENTRY/FARM RETURN")

    old_simple = '''def build_simple_map_profile(left, right, safe, threshold=0.6):\n    \"\"\"Build one SIMPLE maps.json profile from three detected minimap points.\"\"\"\n    lx, ly = left\n    rx, ry = right\n    sx, sy = safe\n    return {\n        \"FARM_TYPE\": \"SIMPLE\",\n        \"LEFT_X\": int(round(float(lx))),\n        \"LEFT_Y\": int(round(float(ly))),\n        \"RIGHT_X\": int(round(float(rx))),\n        \"RIGHT_Y\": int(round(float(ry))),\n        \"SAFE_PLACE_X\": int(round(float(sx))),\n        \"SAFE_PLACE_Y\": int(round(float(sy))),\n        \"CHAR_MATCH_THRESHOLD\": float(threshold),\n    }\n'''
    new_simple = '''def build_simple_map_profile(left, right, safe, threshold=0.6, *, safe_entry=None):\n    \"\"\"Build one SIMPLE maps.json profile from detected minimap points.\"\"\"\n    lx, ly = left\n    rx, ry = right\n    sx, sy = safe\n    profile = {\n        \"FARM_TYPE\": \"SIMPLE\",\n        \"LEFT_X\": int(round(float(lx))),\n        \"LEFT_Y\": int(round(float(ly))),\n        \"RIGHT_X\": int(round(float(rx))),\n        \"RIGHT_Y\": int(round(float(ry))),\n        \"SAFE_PLACE_X\": int(round(float(sx))),\n        \"SAFE_PLACE_Y\": int(round(float(sy))),\n        \"CHAR_MATCH_THRESHOLD\": float(threshold),\n    }\n    if safe_entry is not None:\n        ex, ey = safe_entry\n        profile[\"SAFE_ENTRY_X\"] = int(round(float(ex)))\n        profile[\"SAFE_ENTRY_Y\"] = int(round(float(ey)))\n    return profile\n'''
    text = _replace_once(text, old_simple, new_simple, "simple profile builder")

    old_pirate = '''def build_pirate_map_profile(\n    left, right, safe, loot_left, loot_right, loot_bot_1, loot_bot_2, threshold=0.6\n):\n    \"\"\"Build one Pirate-route profile from captured farm and bottom-loot points.\"\"\"\n    lx, ly = left\n    rx, ry = right\n    sx, sy = safe\n    llx, lly = loot_left\n    lrx, lry = loot_right\n    l1x, l1y = loot_bot_1\n    l2x, l2y = loot_bot_2\n    return {\n        \"FARM_TYPE\": \"PIRATE_ROUTE\",\n        \"LEFT_X\": int(round(float(lx))),\n        \"LEFT_Y\": int(round(float(ly))),\n        \"RIGHT_X\": int(round(float(rx))),\n        \"RIGHT_Y\": int(round(float(ry))),\n        \"SAFE_PLACE_X\": int(round(float(sx))),\n        \"SAFE_PLACE_Y\": int(round(float(sy))),\n        \"LOOT_BOT_LEFT_X\": int(round(float(llx))),\n        \"LOOT_BOT_LEFT_Y\": int(round(float(lly))),\n        \"LOOT_BOT_RIGHT_X\": int(round(float(lrx))),\n        \"LOOT_BOT_RIGHT_Y\": int(round(float(lry))),\n        \"LOOT_BOT_1_X\": int(round(float(l1x))),\n        \"LOOT_BOT_1_Y\": int(round(float(l1y))),\n        \"LOOT_BOT_2_X\": int(round(float(l2x))),\n        \"LOOT_BOT_2_Y\": int(round(float(l2y))),\n        \"CHAR_MATCH_THRESHOLD\": float(threshold),\n    }\n'''
    new_pirate = '''def build_pirate_map_profile(\n    left, right, safe, loot_left, loot_right, loot_bot_1, loot_bot_2, threshold=0.6, *, safe_entry=None\n):\n    \"\"\"Build one Pirate-route profile from captured farm and bottom-loot points.\"\"\"\n    lx, ly = left\n    rx, ry = right\n    sx, sy = safe\n    llx, lly = loot_left\n    lrx, lry = loot_right\n    l1x, l1y = loot_bot_1\n    l2x, l2y = loot_bot_2\n    profile = {\n        \"FARM_TYPE\": \"PIRATE_ROUTE\",\n        \"LEFT_X\": int(round(float(lx))),\n        \"LEFT_Y\": int(round(float(ly))),\n        \"RIGHT_X\": int(round(float(rx))),\n        \"RIGHT_Y\": int(round(float(ry))),\n        \"SAFE_PLACE_X\": int(round(float(sx))),\n        \"SAFE_PLACE_Y\": int(round(float(sy))),\n        \"LOOT_BOT_LEFT_X\": int(round(float(llx))),\n        \"LOOT_BOT_LEFT_Y\": int(round(float(lly))),\n        \"LOOT_BOT_RIGHT_X\": int(round(float(lrx))),\n        \"LOOT_BOT_RIGHT_Y\": int(round(float(lry))),\n        \"LOOT_BOT_1_X\": int(round(float(l1x))),\n        \"LOOT_BOT_1_Y\": int(round(float(l1y))),\n        \"LOOT_BOT_2_X\": int(round(float(l2x))),\n        \"LOOT_BOT_2_Y\": int(round(float(l2y))),\n        \"CHAR_MATCH_THRESHOLD\": float(threshold),\n    }\n    if safe_entry is not None:\n        ex, ey = safe_entry\n        profile[\"SAFE_ENTRY_X\"] = int(round(float(ex)))\n        profile[\"SAFE_ENTRY_Y\"] = int(round(float(ey)))\n    return profile\n'''
    text = _replace_once(text, old_pirate, new_pirate, "pirate profile builder")

    text = _replace_once(
        text,
        '            \"SAFE\": \"SAFE\",\n',
        '            \"SAFE_ENTRY\": \"SAFE ENTRY\",\n            \"SAFE\": \"SAFE\",\n',
        "custom map SAFE ENTRY label",
    )
    text = _replace_count(
        text,
        '(\"LEFT\", \"RIGHT\", \"SAFE\")',
        '(\"LEFT\", \"RIGHT\", \"SAFE_ENTRY\", \"SAFE\")',
        2,
        "custom map FARM button/value order",
    )

    text = _replace_once(
        text,
        '''                        custom_adaptive_y=custom_adaptive_y.get(),\n                    )\n''',
        '''                        custom_adaptive_y=custom_adaptive_y.get(),\n                        safe_entry=captured[\"SAFE_ENTRY\"],\n                    )\n''',
        "V10 custom map SAFE ENTRY serialization",
    )
    text = _replace_once(
        text,
        '''                        captured[\"LOOT_BOT_1\"], captured[\"LOOT_BOT_2\"], 0.6,\n                    )\n''',
        '''                        captured[\"LOOT_BOT_1\"], captured[\"LOOT_BOT_2\"], 0.6,\n                        safe_entry=captured[\"SAFE_ENTRY\"],\n                    )\n''',
        "legacy pirate custom map SAFE ENTRY serialization",
    )
    text = _replace_once(
        text,
        '''                        captured[\"LEFT\"], captured[\"RIGHT\"], captured[\"SAFE\"], 0.6\n                    )\n''',
        '''                        captured[\"LEFT\"], captured[\"RIGHT\"], captured[\"SAFE\"], 0.6,\n                        safe_entry=captured[\"SAFE_ENTRY\"]\n                    )\n''',
        "simple custom map SAFE ENTRY serialization",
    )

    sell_anchor = '    def _spotify_mainfarm_sell_safe_stage(self, cfg, map_pos, now, owner="SUPERVISOR"):\n'
    helpers = '''    # V10.0.17_SAFE_ENTRY_RETURN\n    def _spotify_reset_custom_safe_entry_state(self):\n        self.spotify_custom_safe_entry_state = \"MOVE_ENTRY\"\n        self.spotify_custom_safe_entry_jump_at = 0.0\n\n    def _spotify_custom_safe_entry_step(self, cfg, map_pos, now):\n        profile = cfg.get(\"map_profile\") or {}\n        entry_x = profile.get(\"SAFE_ENTRY_X\")\n        entry_y = profile.get(\"SAFE_ENTRY_Y\")\n        if entry_x is None or entry_y is None:\n            return \"READY\"\n\n        state = str(getattr(self, \"spotify_custom_safe_entry_state\", \"MOVE_ENTRY\") or \"MOVE_ENTRY\")\n        if state == \"DONE\":\n            return \"READY\"\n        if state == \"WAIT_CLIMB\":\n            self.behavior_engine.release_inputs()\n            if float(now) - float(getattr(self, \"spotify_custom_safe_entry_jump_at\", 0.0)) < 0.30:\n                return \"PENDING\"\n            self.spotify_custom_safe_entry_state = \"DONE\"\n            return \"READY\"\n\n        reached = bool(self.behavior_engine.core._spotify_move_to_step(\n            cfg, map_pos, float(entry_x), float(entry_y), float(now),\n            tolerance_x=5.0, tolerance_y=8.0, check_stuck=False, flash_range=9999.0,\n        ))\n        if not reached:\n            return \"PENDING\"\n\n        self.behavior_engine.release_inputs()\n        if not cfg.get(\"jump_key\"):\n            self._spotify_reset_custom_safe_entry_state()\n            return \"FAILED\"\n        if not bool(self.behavior_engine.core._spotify_jump_up(cfg)):\n            self._spotify_reset_custom_safe_entry_state()\n            return \"FAILED\"\n        self.spotify_custom_safe_entry_state = \"WAIT_CLIMB\"\n        self.spotify_custom_safe_entry_jump_at = float(now)\n        return \"PENDING\"\n\n'''
    text = _replace_once(text, sell_anchor, helpers + sell_anchor, "SAFE ENTRY controller methods")

    old_stage = '''    def _spotify_mainfarm_sell_safe_stage(self, cfg, map_pos, now, owner=\"SUPERVISOR\"):\n        if owner == \"MAIN_FARM\":\n            self._c2_trace_emit(\"stage\", name=\"SELL_SAFE\")\n        timer_mode = bool(cfg.get(\"auto_sell_timer_enabled\"))\n        timer_due = self.spotify_sell_timer_event.is_set()\n        full_bag_due = self.spotify_full_bag_event.is_set()\n        trigger_due = timer_due if timer_mode else full_bag_due\n        cooldown_ok = (now - self.last_sell_time) * 1000 >= cfg[\"sell_cooldown\"]\n        sell_requested = bool(cfg.get(\"auto_sell\") and cooldown_ok and trigger_due)\n        if not sell_requested:\n            return CONTINUE\n\n        if getattr(self, \"spotify_r54_safe_state\", \"MOVE_SAFE\") == \"SAFE_FAIL\":\n            self.behavior_engine.core._spotify_reset_safe_place_state()\n        p = cfg.get(\"map_profile\") or {}\n        has_safe = p.get(\"SAFE_PLACE_X\") is not None and p.get(\"SAFE_PLACE_Y\") is not None\n        safe_outcome = self.behavior_engine.safe_place_step(cfg, map_pos, now) if has_safe else \"FAILED\"\n        if safe_outcome == \"READY\":\n            self.spotify_full_bag_event.clear()\n            if not self.spotify_sell_inflight:\n                self.spotify_sell_timer_event.clear()\n                self.spotify_sell_inflight = True\n                # Atomic handoff: SAFE navigation is complete; block C2 before\n                # the asynchronous seller thread can take UI/input ownership.\n                self._c2_pause_add(\"sell\")\n                try:\n                    self.run_sell_thread(cfg)\n                except Exception:\n                    self.spotify_sell_inflight = False\n                    self._c2_pause_remove(\"sell\")\n                    raise\n            self.behavior_engine.core._spotify_reset_safe_place_state()\n        elif safe_outcome == \"FAILED\":\n            self.spotify_full_bag_event.clear()\n            self.spotify_sell_timer_event.clear()\n            self.last_sell_time = now\n            self.behavior_engine.release_inputs()\n            self._log(\"[Spotify Safe] Xác minh SAFE_PLACE thất bại; hủy lượt bán.\")\n        return STOP_TICK\n'''
    new_stage = '''    def _spotify_mainfarm_sell_safe_stage(self, cfg, map_pos, now, owner=\"SUPERVISOR\"):\n        if owner == \"MAIN_FARM\":\n            self._c2_trace_emit(\"stage\", name=\"SELL_SAFE\")\n        timer_mode = bool(cfg.get(\"auto_sell_timer_enabled\"))\n        timer_due = self.spotify_sell_timer_event.is_set()\n        full_bag_due = self.spotify_full_bag_event.is_set()\n        trigger_due = timer_due if timer_mode else full_bag_due\n        cooldown_ok = (now - self.last_sell_time) * 1000 >= cfg[\"sell_cooldown\"]\n        sell_requested = bool(cfg.get(\"auto_sell\") and cooldown_ok and trigger_due)\n        if not sell_requested:\n            return CONTINUE\n\n        reset_entry = getattr(self, \"_spotify_reset_custom_safe_entry_state\", None)\n        entry_step = getattr(self, \"_spotify_custom_safe_entry_step\", None)\n        entry_outcome = entry_step(cfg, map_pos, now) if callable(entry_step) else \"READY\"\n        if entry_outcome == \"PENDING\":\n            return STOP_TICK\n        if entry_outcome == \"FAILED\":\n            self.spotify_full_bag_event.clear()\n            self.spotify_sell_timer_event.clear()\n            self.last_sell_time = now\n            self.behavior_engine.release_inputs()\n            if callable(reset_entry):\n                reset_entry()\n            self.behavior_engine.core._spotify_reset_safe_place_state()\n            self._log(\"[Custom SAFE ENTRY] Không leo được từ SAFE ENTRY; hủy lượt bán.\")\n            return STOP_TICK\n\n        if getattr(self, \"spotify_r54_safe_state\", \"MOVE_SAFE\") == \"SAFE_FAIL\":\n            self.behavior_engine.core._spotify_reset_safe_place_state()\n        p = cfg.get(\"map_profile\") or {}\n        has_safe = p.get(\"SAFE_PLACE_X\") is not None and p.get(\"SAFE_PLACE_Y\") is not None\n        safe_outcome = self.behavior_engine.safe_place_step(cfg, map_pos, now) if has_safe else \"FAILED\"\n        if safe_outcome == \"READY\":\n            self.spotify_full_bag_event.clear()\n            if not self.spotify_sell_inflight:\n                self.spotify_sell_timer_event.clear()\n                self.spotify_sell_inflight = True\n                # Atomic handoff: SAFE navigation is complete; block C2 before\n                # the asynchronous seller thread can take UI/input ownership.\n                self._c2_pause_add(\"sell\")\n                try:\n                    self.run_sell_thread(cfg)\n                except Exception:\n                    self.spotify_sell_inflight = False\n                    self._c2_pause_remove(\"sell\")\n                    raise\n            self.behavior_engine.core._spotify_reset_safe_place_state()\n            if callable(reset_entry):\n                reset_entry()\n        elif safe_outcome == \"FAILED\":\n            self.spotify_full_bag_event.clear()\n            self.spotify_sell_timer_event.clear()\n            self.last_sell_time = now\n            self.behavior_engine.release_inputs()\n            if callable(reset_entry):\n                reset_entry()\n            self._log(\"[Spotify Safe] Xác minh SAFE_PLACE thất bại; hủy lượt bán.\")\n        return STOP_TICK\n'''
    text = _replace_once(text, old_stage, new_stage, "sell-safe SAFE ENTRY integration")

    worker_anchor = '''                    self.spotify_watchdog.notify_sell_completed(completed_at)\n                    self.spotify_sell_timer_event.clear()\n                    self.spotify_sell_inflight = False\n                    self._log(\"[Auto Sell] MiuMiu parity hoàn tất.\")\n'''
    worker_new = '''                    self.spotify_watchdog.notify_sell_completed(completed_at)\n                    self.spotify_sell_timer_event.clear()\n                    strategy = getattr(self, \"strategy_v10\", None)\n                    request_return = getattr(strategy, \"request_post_sell_return_to_farm\", None)\n                    if bool(getattr(strategy, \"running\", False)) and callable(request_return) and request_return():\n                        self._log(\"[Custom Return To Farm] MiuMiu xong → căn X SAFE ENTRY rồi ↓+Jump xuống tầng farm.\")\n                    self.spotify_sell_inflight = False\n                    self._log(\"[Auto Sell] MiuMiu parity hoàn tất.\")\n'''
    text = _replace_once(text, worker_anchor, worker_new, "MiuMiu success return handoff")

    path.write_text(text, encoding="utf-8")


def _patch_strategy(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return
    if "SAFE_ENTRY_X" in text or "FARM_RETURN" in text:
        raise SystemExit("V10.0.17 strategy must start from exact V10.0.15 without SAFE ENTRY/FARM RETURN")

    text = _replace_once(
        text,
        '''    safe: Tuple[float, float]\n    loot_left: Optional[Tuple[float, float]] = None\n''',
        '''    safe: Tuple[float, float]\n    safe_entry: Optional[Tuple[float, float]] = None\n    loot_left: Optional[Tuple[float, float]] = None\n''',
        "resolved SAFE ENTRY field",
    )

    resolver_anchor = '''    values = {name: _number(profile, name) for name in BASE_ROUTE_FIELDS}\n    loot = {name: _number(profile, name) for name in BOTTOM_LOOT_FIELDS} if loot_mode == \"PIRATE_BOTTOM_CUSTOM\" else {}\n    return V10ResolvedProfile(\n'''
    resolver_new = '''    values = {name: _number(profile, name) for name in BASE_ROUTE_FIELDS}\n    loot = {name: _number(profile, name) for name in BOTTOM_LOOT_FIELDS} if loot_mode == \"PIRATE_BOTTOM_CUSTOM\" else {}\n    has_entry_x = profile.get(\"SAFE_ENTRY_X\") is not None\n    has_entry_y = profile.get(\"SAFE_ENTRY_Y\") is not None\n    if has_entry_x != has_entry_y:\n        raise V10ProfileError(\"SAFE ENTRY cần đủ SAFE_ENTRY_X và SAFE_ENTRY_Y\")\n    safe_entry = (\n        (_number(profile, \"SAFE_ENTRY_X\"), _number(profile, \"SAFE_ENTRY_Y\"))\n        if has_entry_x else None\n    )\n    return V10ResolvedProfile(\n'''
    text = _replace_once(text, resolver_anchor, resolver_new, "resolve optional SAFE ENTRY")
    text = _replace_once(
        text,
        '''        safe=(values[\"SAFE_PLACE_X\"], values[\"SAFE_PLACE_Y\"]),\n        loot_left=''',
        '''        safe=(values[\"SAFE_PLACE_X\"], values[\"SAFE_PLACE_Y\"]),\n        safe_entry=safe_entry,\n        loot_left=''',
        "resolved SAFE ENTRY assignment",
    )

    text = _replace_once(
        text,
        '''    *, custom_simple_human=False, custom_fall_recovery=False,\n    custom_loot_jitter=False, custom_adaptive_y=False,\n):\n''',
        '''    *, custom_simple_human=False, custom_fall_recovery=False,\n    custom_loot_jitter=False, custom_adaptive_y=False, safe_entry=None,\n):\n''',
        "V10 builder SAFE ENTRY signature",
    )
    builder_profile_end = '''        \"CUSTOM_LOOT_JITTER\": bool(custom_loot_jitter),\n        \"CUSTOM_ADAPTIVE_Y\": bool(custom_adaptive_y),\n    }\n    if loot_mode_norm == \"PIRATE_BOTTOM_CUSTOM\":\n'''
    builder_profile_new = '''        \"CUSTOM_LOOT_JITTER\": bool(custom_loot_jitter),\n        \"CUSTOM_ADAPTIVE_Y\": bool(custom_adaptive_y),\n    }\n    if safe_entry is not None:\n        ex, ey = safe_entry\n        profile[\"SAFE_ENTRY_X\"] = int(round(float(ex)))\n        profile[\"SAFE_ENTRY_Y\"] = int(round(float(ey)))\n    if loot_mode_norm == \"PIRATE_BOTTOM_CUSTOM\":\n'''
    text = _replace_once(text, builder_profile_end, builder_profile_new, "V10 builder SAFE ENTRY serialization")

    start_anchor = '''        self.fall_off_since = None\n        self.next_fall_recovery_at = now\n        self.last_position = None\n'''
    start_new = '''        self.fall_off_since = None\n        self.next_fall_recovery_at = now\n        self.return_to_farm_pending = False\n        self.return_to_farm_state = \"MOVE_ENTRY\"\n        self.return_to_farm_drop_at = 0.0\n        self.return_to_farm_attempts = 0\n        self.return_to_farm_failed_logged = False\n        self.last_position = None\n'''
    text = _replace_once(text, start_anchor, start_new, "return state start reset")

    tick_anchor = "    def tick(self, cfg: Mapping[str, Any], map_pos, now: float) -> bool:\n"
    methods = '''    # V10.0.17_SAFE_ENTRY_RETURN\n    def request_post_sell_return_to_farm(self) -> bool:\n        resolved = self.resolved\n        if not self.running or resolved is None or resolved.safe_entry is None:\n            return False\n        self.return_to_farm_pending = True\n        self.return_to_farm_state = \"MOVE_ENTRY\"\n        self.return_to_farm_drop_at = 0.0\n        self.return_to_farm_attempts = 0\n        self.return_to_farm_failed_logged = False\n        self.release_inputs()\n        return True\n\n    def _finish_post_sell_return_to_farm(self) -> None:\n        self.release_inputs()\n        self.return_to_farm_pending = False\n        self.return_to_farm_state = \"MOVE_ENTRY\"\n        self.return_to_farm_drop_at = 0.0\n        self.return_to_farm_attempts = 0\n        self.return_to_farm_failed_logged = False\n        self.fall_off_since = None\n\n    def _fail_post_sell_return_to_farm(self, message: str) -> None:\n        self.release_inputs()\n        self.return_to_farm_state = \"FAILED\"\n        if not bool(getattr(self, \"return_to_farm_failed_logged\", False)):\n            self.return_to_farm_failed_logged = True\n            try:\n                self.host._log(f\"[Custom Return To Farm] {message}\")\n            except Exception:\n                pass\n\n    def _post_sell_return_to_farm_step(self, cfg: Mapping[str, Any], map_pos, now: float) -> bool:\n        resolved = self.resolved\n        if resolved is None or resolved.safe_entry is None or not bool(getattr(self, \"return_to_farm_pending\", False)):\n            return False\n\n        sell_lock = getattr(self.host, \"sell_lock\", None)\n        lock_held = bool(\n            sell_lock is not None\n            and callable(getattr(sell_lock, \"locked\", None))\n            and sell_lock.locked()\n        )\n        if bool(getattr(self.host, \"spotify_sell_inflight\", False)) or lock_held:\n            self.release_inputs()\n            return True\n\n        px, py = float(map_pos[0]), float(map_pos[1])\n        adaptive = bool((self.profile or {}).get(\"CUSTOM_ADAPTIVE_Y\"))\n        anchor = getattr(self, \"adaptive_y_anchor\", None)\n        lane_y = (\n            float(anchor)\n            if adaptive and anchor is not None\n            else (float(resolved.left[1]) + float(resolved.right[1])) / 2.0\n        )\n        band = float(getattr(self, \"FALL_RECOVERY_BAND\", 12.0))\n        if abs(py - lane_y) <= band:\n            self._finish_post_sell_return_to_farm()\n            return False\n\n        state = str(getattr(self, \"return_to_farm_state\", \"MOVE_ENTRY\") or \"MOVE_ENTRY\")\n        if state == \"FAILED\":\n            self.release_inputs()\n            return True\n\n        target_x = float(resolved.safe_entry[0])\n        if state == \"MOVE_ENTRY\":\n            self._release_attack_hold()\n            if abs(px - target_x) > float(getattr(self, \"EDGE_TOLERANCE\", 5.0)):\n                key = cfg.get(\"right_key\", \"RIGHT\") if px < target_x else cfg.get(\"left_key\", \"LEFT\")\n                self.host.set_move(key)\n                return True\n\n            self.release_inputs()\n            if not cfg.get(\"jump_key\"):\n                self._fail_post_sell_return_to_farm(\"thiếu Jump key; giữ bot tạm dừng trên SAFE.\")\n                return True\n            ok = bool(self.host.behavior_engine.core._spotify_jump_down_reconstructed(cfg))\n            if not ok:\n                self._fail_post_sell_return_to_farm(\"↓ + Jump không gửi được; giữ bot tạm dừng trên SAFE.\")\n                return True\n            self.return_to_farm_attempts = int(getattr(self, \"return_to_farm_attempts\", 0)) + 1\n            self.return_to_farm_drop_at = float(now)\n            self.return_to_farm_state = \"WAIT_DROP\"\n            return True\n\n        self.release_inputs()\n        drop_at = float(getattr(self, \"return_to_farm_drop_at\", 0.0))\n        elapsed = float(now) - drop_at\n        if elapsed < 0.45:\n            return True\n        if abs(py - lane_y) <= band:\n            self._finish_post_sell_return_to_farm()\n            return False\n        if elapsed >= 1.20:\n            if int(getattr(self, \"return_to_farm_attempts\", 0)) >= 4:\n                self._fail_post_sell_return_to_farm(\"không xác nhận được Y tầng farm sau 4 lần ↓ + Jump; không farm mù.\")\n                return True\n            self.return_to_farm_state = \"MOVE_ENTRY\"\n        return True\n\n'''
    text = _replace_once(text, tick_anchor, methods + tick_anchor, "return-to-farm methods")

    map_guard = '''        if map_pos is None:\n            self.release_inputs()\n            return False\n'''
    map_guard_new = map_guard + '''        if bool(getattr(self, \"return_to_farm_pending\", False)):\n            if self._post_sell_return_to_farm_step(cfg, map_pos, now):\n                return True\n'''
    text = _replace_once(text, map_guard, map_guard_new, "return owner before normal farm")

    path.write_text(text, encoding="utf-8")


def _patch_ui(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "V10.0.17" in text:
        return
    if "V10.0.15" not in text:
        raise SystemExit("V10.0.17 UI patch expected exact V10.0.15 UI")
    text = text.replace("10.0.15", "10.0.17")
    path.write_text(text, encoding="utf-8")


def apply_v1017(app_dir: Path) -> None:
    app_dir = Path(app_dir)
    controller = app_dir / "maple_nghia_pro.py"
    strategy = app_dir / "nghia_strategy_v10.py"
    ui = app_dir / "nghia_spotify_nologin.py"
    for path in (controller, strategy, ui):
        if not path.is_file():
            raise SystemExit(f"V10.0.17 base missing {path}")
    _patch_controller(controller)
    _patch_strategy(strategy)
    _patch_ui(ui)
    print("V1017_SAFE_ENTRY_RETURN_PATCH_OK")


if __name__ == "__main__":
    apply_v1017(Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload"))
