from __future__ import annotations

from dataclasses import dataclass
import random
import threading
import time
from typing import Any, Mapping, Optional, Tuple

try:
    import mss  # type: ignore
except Exception:  # pragma: no cover - optional capture acceleration
    mss = None

ENGINE_MARKER = "STRATEGY_V10"
FARM_TYPES = {"PIRATE_ROUTE"}
COMBAT_MODES = {"SPOTIFY_COMBO", "HOLD_SKILL_1", "SPAM_SKILL", "PIRATE_1HIT", "STAND_STILL"}
TP_MODES = {"NONE", "ROUTE_TP", "SPAM_TP_SKILL", "ADAPTIVE_Y"}
LOOT_MODES = {"NONE", "SIMPLE", "PIRATE_BOTTOM_CUSTOM"}
BASE_ROUTE_FIELDS = (
    "LEFT_X", "LEFT_Y", "RIGHT_X", "RIGHT_Y", "SAFE_PLACE_X", "SAFE_PLACE_Y",
)
BOTTOM_LOOT_FIELDS = (
    "LOOT_BOT_LEFT_X", "LOOT_BOT_LEFT_Y", "LOOT_BOT_RIGHT_X", "LOOT_BOT_RIGHT_Y",
    "LOOT_BOT_1_X", "LOOT_BOT_1_Y", "LOOT_BOT_2_X", "LOOT_BOT_2_Y",
)


class V10ProfileError(ValueError):
    pass


@dataclass(frozen=True)
class V10ResolvedProfile:
    farm_type: str
    combat_mode: str
    tp_mode: str
    loot_mode: str
    left: Tuple[float, float]
    right: Tuple[float, float]
    safe: Tuple[float, float]
    loot_left: Optional[Tuple[float, float]] = None
    loot_right: Optional[Tuple[float, float]] = None
    loot_1: Optional[Tuple[float, float]] = None
    loot_2: Optional[Tuple[float, float]] = None


def _norm(value: Any) -> str:
    return str(value or "").strip().upper()


def is_v10_profile(profile: Mapping[str, Any] | None) -> bool:
    return _norm((profile or {}).get("ENGINE_MODE")) == ENGINE_MARKER


def _number(profile: Mapping[str, Any], name: str) -> float:
    if name not in profile or profile.get(name) is None:
        raise V10ProfileError(f"Thiếu field bắt buộc: {name}")
    try:
        return float(profile[name])
    except Exception as exc:
        raise V10ProfileError(f"Field {name} phải là số") from exc


def _enum(profile: Mapping[str, Any], name: str, allowed: set[str]) -> str:
    value = _norm(profile.get(name))
    if not value:
        raise V10ProfileError(f"Thiếu field bắt buộc: {name}")
    if value not in allowed:
        raise V10ProfileError(f"{name} không hợp lệ: {value}")
    return value


def resolve_v10_profile(profile: Mapping[str, Any]) -> V10ResolvedProfile:
    if not is_v10_profile(profile):
        raise V10ProfileError("Profile không có ENGINE_MODE=STRATEGY_V10")
    farm_type = _enum(profile, "FARM_TYPE", FARM_TYPES)
    combat_mode = _enum(profile, "COMBAT_MODE", COMBAT_MODES)
    tp_mode = _enum(profile, "TP_MODE", TP_MODES)
    loot_mode = _enum(profile, "LOOT_MODE", LOOT_MODES)
    values = {name: _number(profile, name) for name in BASE_ROUTE_FIELDS}
    loot = {name: _number(profile, name) for name in BOTTOM_LOOT_FIELDS} if loot_mode == "PIRATE_BOTTOM_CUSTOM" else {}
    return V10ResolvedProfile(
        farm_type=farm_type,
        combat_mode=combat_mode,
        tp_mode=tp_mode,
        loot_mode=loot_mode,
        left=(values["LEFT_X"], values["LEFT_Y"]),
        right=(values["RIGHT_X"], values["RIGHT_Y"]),
        safe=(values["SAFE_PLACE_X"], values["SAFE_PLACE_Y"]),
        loot_left=(loot["LOOT_BOT_LEFT_X"], loot["LOOT_BOT_LEFT_Y"]) if loot else None,
        loot_right=(loot["LOOT_BOT_RIGHT_X"], loot["LOOT_BOT_RIGHT_Y"]) if loot else None,
        loot_1=(loot["LOOT_BOT_1_X"], loot["LOOT_BOT_1_Y"]) if loot else None,
        loot_2=(loot["LOOT_BOT_2_X"], loot["LOOT_BOT_2_Y"]) if loot else None,
    )


def custom_bottom_route_points(profile: Mapping[str, Any], direction: int = 1) -> list[tuple[int, int]]:
    resolved = resolve_v10_profile(profile)
    if resolved.loot_mode != "PIRATE_BOTTOM_CUSTOM":
        raise V10ProfileError("LOOT_MODE hiện tại không phải PIRATE_BOTTOM_CUSTOM")
    forward = [resolved.loot_left, resolved.loot_1, resolved.loot_2, resolved.loot_right]
    pts = forward if direction >= 0 else list(reversed(forward))
    return [(int(round(x)), int(round(y))) for x, y in pts if x is not None and y is not None]


def build_v10_pirate_profile(
    left, right, safe, loot_left, loot_right, loot_bot_1, loot_bot_2,
    combat_mode="SPOTIFY_COMBO", tp_mode="SPAM_TP_SKILL",
    loot_mode="PIRATE_BOTTOM_CUSTOM", threshold=0.6,
):
    lx, ly = left; rx, ry = right; sx, sy = safe
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
    }
    resolve_v10_profile(profile)
    return profile


def legacy_neutral_map_profile() -> dict[str, Any]:
    return {"FARM_TYPE": "V10_ISOLATED"}


class V10StrategyEngine:
    EDGE_TOLERANCE = 5.0
    ROUTE_TP_INTERVAL = 0.45
    SPAM_TP_INTERVAL = 0.16
    SPAM_SKILL_INTERVAL = 0.09
    STAND_SKILL_INTERVAL = 0.45
    SIMPLE_LOOT_MIN_INTERVAL = 1.0
    ADAPTIVE_Y_HARD_BAND = 12.0
    ADAPTIVE_Y_ACTION_INTERVAL = 0.40

    def __init__(self, host: Any):
        self.host = host
        self.input_lock = host.behavior_engine.input_lock
        self.running = False
        self.generation = 0
        self.thread: Optional[threading.Thread] = None
        self.resolved: Optional[V10ResolvedProfile] = None
        self.profile: dict[str, Any] = {}
        self.cfg: dict[str, Any] = {}
        self.direction = 1
        self.loot_direction = 1
        self.loot_state = "FARM"
        self.loot_index = 0
        self.next_loot_at = 0.0
        self.next_combat_at = 0.0
        self.next_tp_at = 0.0
        self.next_adaptive_action_at = 0.0
        self.adaptive_y_anchor: Optional[float] = None
        self.held_attack_key: Optional[str] = None
        self.last_position = None

    @staticmethod
    def is_runtime_cfg(cfg: Mapping[str, Any] | None) -> bool:
        cfg = cfg or {}
        return _norm(cfg.get("engine_mode")) == ENGINE_MARKER and is_v10_profile(cfg.get("v10_profile") or {})

    @staticmethod
    def validate_runtime_cfg(cfg: Mapping[str, Any]) -> V10ResolvedProfile:
        profile = cfg.get("v10_profile") or {}
        return resolve_v10_profile(profile)

    def _release_attack_hold(self) -> None:
        key = self.held_attack_key
        self.held_attack_key = None
        if key:
            try:
                self.host._input_key_up(key)
            except Exception:
                pass

    def release_inputs(self) -> None:
        with self.input_lock:
            self._release_attack_hold()
            try:
                self.host.release_move()
            except Exception:
                pass

    def start(self, cfg: Mapping[str, Any]) -> None:
        resolved = self.validate_runtime_cfg(cfg)
        self.stop()
        self.resolved = resolved
        self.profile = dict(cfg.get("v10_profile") or {})
        self.cfg = dict(cfg)
        self.cfg["map_profile"] = dict(self.profile)
        self.cfg["farm_type"] = resolved.farm_type
        self.running = True
        self.generation += 1
        generation = self.generation
        now = time.monotonic()
        self.direction = 1
        self.loot_direction = 1
        self.loot_state = "FARM"
        self.loot_index = 0
        self.next_loot_at = now + self._loot_delay(self.cfg)
        self.next_combat_at = now
        self.next_tp_at = now
        self.next_adaptive_action_at = now
        self.adaptive_y_anchor = None
        self.last_position = None
        self.thread = threading.Thread(
            target=self._worker, args=(generation,), daemon=True, name="Nghia-V10-Strategy"
        )
        self.thread.start()

    def stop(self) -> None:
        was_active = bool(self.running or self.held_attack_key)
        self.running = False
        self.generation += 1
        if was_active:
            self.release_inputs()

    def _loot_delay(self, cfg: Mapping[str, Any]) -> float:
        try:
            base = float(cfg.get("loot_time", cfg.get("spotify_loot_time", 90.0)) or 90.0)
        except Exception:
            base = 90.0
        return max(self.SIMPLE_LOOT_MIN_INTERVAL, base)

    def _worker(self, generation: int) -> None:
        capture = None
        hwnd = None
        last_focus_refresh = 0.0
        try:
            if mss is not None:
                capture = mss.mss()
            while self.running and generation == self.generation and bool(getattr(self.host, "running", True)):
                cfg = dict(self.cfg)
                now = time.monotonic()
                if now - last_focus_refresh >= 0.20:
                    last_focus_refresh = now
                    refresher = getattr(self.host, "_spotify_focus_refresh", None)
                    if callable(refresher):
                        try:
                            refresher(cfg, force=bool(cfg.get("spotify_force_focus_parity", False)))
                        except Exception:
                            pass
                cached = getattr(self.host, "_spotify_cached_game_hwnd", None)
                if callable(cached):
                    hwnd = cached() or hwnd
                if not hwnd:
                    finder = getattr(self.host, "_find_game_window", None)
                    if callable(finder):
                        try:
                            hwnd, _ = finder(cfg.get("window_title", ""))
                        except Exception:
                            hwnd = None
                try:
                    roi = self.host._capture_spotify_minimap_direct(cfg, capture, hwnd)
                    pos = self.host._detect_spotify_player_from_minimap(roi, cfg)
                except Exception:
                    pos = None
                self.last_position = pos
                try:
                    self.tick(cfg, pos, now)
                except Exception as exc:
                    self.release_inputs()
                    try:
                        self.host._log(f"[V10 Strategy] tick error: {exc}")
                    except Exception:
                        pass
                time.sleep(0.01)
        finally:
            try:
                if capture is not None:
                    capture.close()
            except Exception:
                pass
            self.release_inputs()

    def tick(self, cfg: Mapping[str, Any], map_pos, now: float) -> bool:
        resolved = self.resolved
        if not self.running or resolved is None:
            return False
        if bool(cfg.get("pause_on_focus_loss", True)):
            checker = getattr(self.host, "_game_has_focus", None)
            if callable(checker) and not checker(cfg):
                self.release_inputs()
                return False
        if map_pos is None:
            self.release_inputs()
            return False
        if self.loot_state != "FARM":
            return self._custom_loot_step(cfg, map_pos, now)
        if self._maybe_begin_loot(cfg, now):
            return True
        edge_hit = self._farm_route_step(cfg, map_pos, now)
        if resolved.tp_mode == "ADAPTIVE_Y":
            self._adaptive_y_step(cfg, map_pos, now)
        elif resolved.tp_mode in {"ROUTE_TP", "SPAM_TP_SKILL"}:
            self._teleport_step(cfg, map_pos, now)
        self._combat_step(cfg, map_pos, now, edge_hit=edge_hit)
        return True

    def _farm_route_step(self, cfg, map_pos, now: float) -> bool:
        resolved = self.resolved
        assert resolved is not None
        px = float(map_pos[0])
        edge_hit = False
        if resolved.combat_mode == "STAND_STILL":
            self.host.release_move()
            return False
        if self.direction > 0 and px >= resolved.right[0] - self.EDGE_TOLERANCE:
            self.host.release_move(); self.direction = -1; edge_hit = True
        elif self.direction < 0 and px <= resolved.left[0] + self.EDGE_TOLERANCE:
            self.host.release_move(); self.direction = 1; edge_hit = True
        direction_key = cfg.get("right_key", "RIGHT") if self.direction > 0 else cfg.get("left_key", "LEFT")
        self.host.set_move(direction_key)
        return edge_hit

    def _teleport_step(self, cfg, map_pos, now: float) -> bool:
        resolved = self.resolved
        assert resolved is not None
        if resolved.tp_mode == "NONE" or not cfg.get("tele_enabled") or not cfg.get("tele_key"):
            return False
        if resolved.tp_mode == "SPAM_TP_SKILL" and resolved.combat_mode == "SPOTIFY_COMBO":
            return False
        interval = self.SPAM_TP_INTERVAL if resolved.tp_mode == "SPAM_TP_SKILL" else self.ROUTE_TP_INTERVAL
        if now < self.next_tp_at:
            return False
        px = float(map_pos[0])
        remaining = resolved.right[0] - px if self.direction > 0 else px - resolved.left[0]
        if remaining <= 14.0:
            return False
        key = cfg.get("right_key", "RIGHT") if self.direction > 0 else cfg.get("left_key", "LEFT")
        ok = bool(self.host.behavior_engine.core._spotify_tap_combo(
            cfg, key, cfg.get("tele_key"), hold_ms=random.randint(50, 110), role="TELEPORT"
        ))
        self.next_tp_at = time.monotonic() + interval
        return ok

    def _adaptive_y_step(self, cfg, map_pos, now: float) -> bool:
        if now < self.next_adaptive_action_at:
            return False
        py = float(map_pos[1])
        if self.adaptive_y_anchor is None:
            self.adaptive_y_anchor = py
            return False
        delta = py - self.adaptive_y_anchor
        if abs(delta) <= self.ADAPTIVE_Y_HARD_BAND:
            return False
        core = self.host.behavior_engine.core
        ok = False
        if delta < 0:
            if cfg.get("tele_enabled") and cfg.get("tele_key"):
                ok = bool(core._spotify_flash_down(cfg))
            if not ok and cfg.get("jump_key"):
                ok = bool(core._spotify_jump_down_reconstructed(cfg))
        else:
            ok = bool(core._spotify_jump_up(cfg))
        self.next_adaptive_action_at = time.monotonic() + self.ADAPTIVE_Y_ACTION_INTERVAL
        return ok

    def _combat_step(self, cfg, map_pos, now: float, *, edge_hit: bool) -> bool:
        resolved = self.resolved
        assert resolved is not None
        key = str(cfg.get("spotify_attack_key") or "").strip()
        if not key:
            return False
        core = self.host.behavior_engine.core
        direction_key = None if resolved.combat_mode == "STAND_STILL" else (
            cfg.get("right_key", "RIGHT") if self.direction > 0 else cfg.get("left_key", "LEFT")
        )
        if resolved.combat_mode == "HOLD_SKILL_1":
            if self.held_attack_key != key:
                self._release_attack_hold()
                if self.host._input_key_down(key):
                    self.held_attack_key = key
                    return True
            return False
        self._release_attack_hold()
        if resolved.combat_mode == "PIRATE_1HIT":
            if not edge_hit:
                return False
            return bool(core._spotify_input_semantic(cfg, "ATTACK", key, hold_ms=random.randint(50, 150)))
        if now < self.next_combat_at:
            return False
        if resolved.combat_mode == "SPAM_SKILL":
            ok = bool(core._spotify_input_semantic(cfg, "ATTACK", key, hold_ms=random.randint(50, 110)))
            self.next_combat_at = time.monotonic() + self.SPAM_SKILL_INTERVAL
            return ok
        if resolved.combat_mode == "STAND_STILL":
            ok = bool(core._spotify_input_semantic(cfg, "ATTACK", key, hold_ms=random.randint(50, 150)))
            self.next_combat_at = time.monotonic() + self.STAND_SKILL_INTERVAL
            return ok
        flash_key = cfg.get("tele_key") if (resolved.tp_mode == "SPAM_TP_SKILL" and cfg.get("tele_enabled")) else None
        ok = bool(core._spotify_hold_combo_action(
            cfg, direction_key, flash_key, key, random.uniform(0.20, 0.50)
        ))
        self.next_combat_at = time.monotonic()
        return ok

    def _maybe_begin_loot(self, cfg, now: float) -> bool:
        resolved = self.resolved
        assert resolved is not None
        if resolved.loot_mode == "NONE" or not bool(cfg.get("auto_loot", cfg.get("spotify_loot_enabled", False))):
            return False
        if now < self.next_loot_at:
            return False
        self._release_attack_hold()
        self.host.release_move()
        if resolved.loot_mode == "SIMPLE":
            key = str(cfg.get("loot_key") or "").strip()
            if key:
                self.host.behavior_engine.core._spotify_input_semantic(cfg, "LOOT", key, hold_ms=80)
            self.next_loot_at = time.monotonic() + self._loot_delay(cfg)
            return True
        self.loot_state = "CUSTOM_BOTTOM"
        self.loot_index = 0
        return True

    def _custom_loot_step(self, cfg, map_pos, now: float) -> bool:
        resolved = self.resolved
        assert resolved is not None
        points = custom_bottom_route_points(self.profile, self.loot_direction)
        if self.loot_index >= len(points):
            self.loot_state = "FARM"
            self.loot_index = 0
            self.loot_direction *= -1
            self.next_loot_at = time.monotonic() + self._loot_delay(cfg)
            return True
        target = points[self.loot_index]
        route_cfg = dict(cfg)
        if resolved.tp_mode == "NONE":
            route_cfg["tele_enabled"] = False
        arrived = bool(self.host.behavior_engine.core._spotify_move_to_step(
            route_cfg, map_pos, float(target[0]), float(target[1]), now,
            tolerance_x=6.0, tolerance_y=8.0, check_stuck=False, flash_range=999.0,
        ))
        if arrived:
            key = str(cfg.get("loot_key") or "").strip()
            if key:
                self.host.behavior_engine.core._spotify_input_semantic(
                    cfg, "LOOT", key, hold_ms=random.randint(50, 110)
                )
            self.loot_index += 1
            reset = getattr(self.host.behavior_engine.core, "_spotify_reset_move_to_state", None)
            if callable(reset):
                reset()
        return True
