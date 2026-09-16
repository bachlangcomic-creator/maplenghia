from __future__ import annotations

from pathlib import Path
import sys

MARKER = "V10.0.16_RETURN_TO_FARM_AFTER_MIUMIU"


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def _patch_strategy(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return
    if "FARM_RETURN" in text or "_custom_farm_return_step" in text:
        raise SystemExit("V10.0.16 correction must not contain the separate FARM RETURN feature")
    if "safe_entry" not in text or "SAFE_ENTRY_X" not in text:
        raise SystemExit("SAFE ENTRY correction must be applied before RETURN TO FARM overlay")

    tick_anchor = "    def tick(self, cfg: Mapping[str, Any], map_pos, now: float) -> bool:\n"
    methods = '''    # V10.0.16_RETURN_TO_FARM_AFTER_MIUMIU\n    def request_post_sell_return_to_farm(self) -> bool:\n        \"\"\"Queue the Custom Map post-sale route back through SAFE ENTRY.\n\n        This is intentionally distinct from wrong-floor recovery: no extra map\n        coordinate is introduced. The existing SAFE ENTRY X is reused as the\n        drop point after MiuMiu closes.\n        \"\"\"\n        resolved = self.resolved\n        profile = self.profile or {}\n        if resolved is None or profile.get(\"SAFE_ENTRY_X\") is None or profile.get(\"SAFE_ENTRY_Y\") is None:\n            return False\n        self.return_to_farm_pending = True\n        self.return_to_farm_state = \"MOVE_ENTRY\"\n        self.return_to_farm_drop_at = 0.0\n        self.return_to_farm_attempts = 0\n        self.return_to_farm_failed_logged = False\n        self.release_inputs()\n        return True\n\n    def _finish_post_sell_return_to_farm(self) -> None:\n        self.release_inputs()\n        self.return_to_farm_pending = False\n        self.return_to_farm_state = \"MOVE_ENTRY\"\n        self.return_to_farm_drop_at = 0.0\n        self.return_to_farm_attempts = 0\n        self.return_to_farm_failed_logged = False\n        if hasattr(self, \"fall_off_since\"):\n            self.fall_off_since = None\n\n    def _fail_post_sell_return_to_farm(self, message: str) -> None:\n        self.release_inputs()\n        self.return_to_farm_state = \"FAILED\"\n        if not bool(getattr(self, \"return_to_farm_failed_logged\", False)):\n            self.return_to_farm_failed_logged = True\n            try:\n                self.host._log(f\"[Custom Return To Farm] {message}\")\n            except Exception:\n                pass\n\n    def _post_sell_return_to_farm_step(self, cfg: Mapping[str, Any], map_pos, now: float) -> bool:\n        resolved = self.resolved\n        profile = self.profile or {}\n        if (\n            resolved is None\n            or profile.get(\"SAFE_ENTRY_X\") is None\n            or profile.get(\"SAFE_ENTRY_Y\") is None\n            or not bool(getattr(self, \"return_to_farm_pending\", False))\n        ):\n            return False\n\n        # MiuMiu still owns UI/input while its worker or sell lock is active.\n        sell_lock = getattr(self.host, \"sell_lock\", None)\n        lock_held = bool(\n            sell_lock is not None\n            and callable(getattr(sell_lock, \"locked\", None))\n            and sell_lock.locked()\n        )\n        if bool(getattr(self.host, \"spotify_sell_inflight\", False)) or lock_held:\n            self.release_inputs()\n            return True\n\n        px, py = float(map_pos[0]), float(map_pos[1])\n        adaptive = bool(profile.get(\"CUSTOM_ADAPTIVE_Y\"))\n        anchor = getattr(self, \"adaptive_y_anchor\", None)\n        lane_y = (\n            float(anchor)\n            if adaptive and anchor is not None\n            else (float(resolved.left[1]) + float(resolved.right[1])) / 2.0\n        )\n        band = float(getattr(self, \"FALL_RECOVERY_BAND\", 12.0))\n\n        # Resume farming only after minimap Y confirms the farm lane.\n        if abs(py - lane_y) <= band:\n            self._finish_post_sell_return_to_farm()\n            return False\n\n        state = str(getattr(self, \"return_to_farm_state\", \"MOVE_ENTRY\") or \"MOVE_ENTRY\")\n        if state == \"FAILED\":\n            self.release_inputs()\n            return True\n\n        target_x = float(profile[\"SAFE_ENTRY_X\"])\n        if state == \"MOVE_ENTRY\":\n            # Stay on the SAFE floor and align horizontally with SAFE ENTRY X.\n            if abs(px - target_x) > float(getattr(self, \"EDGE_TOLERANCE\", 5.0)):\n                key = cfg.get(\"right_key\", \"RIGHT\") if px < target_x else cfg.get(\"left_key\", \"LEFT\")\n                self.host.set_move(key)\n                return True\n\n            self.release_inputs()\n            if not cfg.get(\"jump_key\"):\n                self._fail_post_sell_return_to_farm(\"thiếu Jump key; giữ bot tạm dừng trên SAFE.\")\n                return True\n            ok = bool(self.host.behavior_engine.core._spotify_jump_down_reconstructed(cfg))\n            if not ok:\n                self._fail_post_sell_return_to_farm(\"↓ + Jump không gửi được; giữ bot tạm dừng trên SAFE.\")\n                return True\n            self.return_to_farm_attempts = int(getattr(self, \"return_to_farm_attempts\", 0)) + 1\n            self.return_to_farm_drop_at = float(now)\n            self.return_to_farm_state = \"WAIT_DROP\"\n            return True\n\n        self.release_inputs()\n        drop_at = float(getattr(self, \"return_to_farm_drop_at\", 0.0))\n        elapsed = float(now) - drop_at\n        if elapsed < 0.45:\n            return True\n        if abs(py - lane_y) <= band:\n            self._finish_post_sell_return_to_farm()\n            return False\n        if elapsed >= 1.20:\n            if int(getattr(self, \"return_to_farm_attempts\", 0)) >= 4:\n                self._fail_post_sell_return_to_farm(\"không xác nhận được Y tầng farm sau 4 lần ↓ + Jump; không farm mù.\")\n                return True\n            self.return_to_farm_state = \"MOVE_ENTRY\"\n        return True\n\n'''
    text = _replace_once(text, tick_anchor, methods + tick_anchor, "strategy method insertion")

    map_guard = '''        if map_pos is None:\n            self.release_inputs()\n            return False\n'''
    map_guard_new = map_guard + '''        if bool(getattr(self, "return_to_farm_pending", False)):\n            if self._post_sell_return_to_farm_step(cfg, map_pos, now):\n                return True\n'''
    text = _replace_once(text, map_guard, map_guard_new, "strategy tick return owner")

    # Ensure a restart can never inherit a stale post-sale return request.
    start_anchor = '''        self.next_fall_recovery_at = now\n        self.last_position = None\n'''
    start_new = '''        self.next_fall_recovery_at = now\n        self.return_to_farm_pending = False\n        self.return_to_farm_state = "MOVE_ENTRY"\n        self.return_to_farm_drop_at = 0.0\n        self.return_to_farm_attempts = 0\n        self.return_to_farm_failed_logged = False\n        self.last_position = None\n'''
    text = _replace_once(text, start_anchor, start_new, "strategy start reset")

    path.write_text(text, encoding="utf-8")


def _patch_controller(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return
    if "FARM_RETURN" in text or "_custom_farm_return_step" in text:
        raise SystemExit("V10.0.16 correction must not contain the separate FARM RETURN feature")
    anchor = '''                    self.spotify_watchdog.notify_sell_completed(completed_at)\n                    self.spotify_sell_timer_event.clear()\n                    self.spotify_sell_inflight = False\n                    self._log("[Auto Sell] MiuMiu parity hoàn tất.")\n'''
    replacement = '''                    self.spotify_watchdog.notify_sell_completed(completed_at)\n                    self.spotify_sell_timer_event.clear()\n                    # V10.0.16_RETURN_TO_FARM_AFTER_MIUMIU\n                    runtime = self.runtime_cfg or cfg\n                    if str(runtime.get("engine_mode", "")).upper() == "STRATEGY_V10":\n                        request_return = getattr(self.strategy_v10, "request_post_sell_return_to_farm", None)\n                        if callable(request_return) and request_return():\n                            self._log("[Custom Return To Farm] MiuMiu xong → về X SAFE ENTRY rồi ↓+Jump xuống tầng farm.")\n                    self.spotify_sell_inflight = False\n                    self._log("[Auto Sell] MiuMiu parity hoàn tất.")\n'''
    text = _replace_once(text, anchor, replacement, "seller success wiring")
    path.write_text(text, encoding="utf-8")


def apply_return_to_farm(app_dir: Path) -> None:
    app_dir = Path(app_dir)
    strategy = app_dir / "nghia_strategy_v10.py"
    controller = app_dir / "maple_nghia_pro.py"
    if not strategy.is_file() or not controller.is_file():
        raise SystemExit(f"V10.0.16 payload missing expected files under {app_dir}")
    _patch_strategy(strategy)
    _patch_controller(controller)
    print("V1016_RETURN_TO_FARM_OVERLAY_OK")


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload")
    apply_return_to_farm(target)
