from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

import pytest

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload")).resolve()
sys.path.insert(0, str(APP))


def _profile(**flags):
    from nghia_strategy_v10 import build_v10_pirate_profile

    return build_v10_pirate_profile(
        (10, 100), (100, 100), (50, 100),
        (10, 120), (100, 120), (35, 120), (75, 120),
        "SPOTIFY_COMBO", "NONE", "PIRATE_BOTTOM_CUSTOM", 0.6,
        **flags,
    )


class FakeCore:
    def __init__(self):
        self.jump_up_calls = 0
        self.flash_down_calls = 0
        self.jump_down_calls = 0
        self.semantic_calls = []

    def _spotify_input_semantic(self, cfg, role, key, hold_ms=0):
        self.semantic_calls.append((role, key, hold_ms))
        return True

    def _spotify_jump_up(self, cfg):
        self.jump_up_calls += 1
        return True

    def _spotify_flash_down(self, cfg):
        self.flash_down_calls += 1
        return True

    def _spotify_jump_down_reconstructed(self, cfg):
        self.jump_down_calls += 1
        return True

    def _spotify_hold_combo_action(self, *args, **kwargs):
        return True

    def _spotify_tap_combo(self, *args, **kwargs):
        return True

    def _spotify_move_to_step(self, *args, **kwargs):
        return False

    def _spotify_reset_move_to_state(self):
        return None


class FakeBehavior:
    def __init__(self):
        self.input_lock = threading.RLock()
        self.core = FakeCore()


class FakeHost:
    def __init__(self):
        self.behavior_engine = FakeBehavior()
        self.running = True
        self.move = None
        self.release_calls = 0

    def set_move(self, key):
        self.move = key

    def release_move(self):
        self.move = None
        self.release_calls += 1

    def _input_key_down(self, key):
        return True

    def _input_key_up(self, key):
        return True

    def _game_has_focus(self, cfg):
        return True

    def _log(self, msg):
        return None


def _engine(profile):
    from nghia_strategy_v10 import V10StrategyEngine, resolve_v10_profile

    host = FakeHost()
    engine = V10StrategyEngine(host)
    engine.profile = dict(profile)
    engine.resolved = resolve_v10_profile(profile)
    engine.running = True
    return engine, host


def test_custom_flags_default_off_and_persist_when_enabled():
    base = _profile()
    for key in (
        "CUSTOM_SIMPLE_HUMAN",
        "CUSTOM_FALL_RECOVERY",
        "CUSTOM_LOOT_JITTER",
        "CUSTOM_ADAPTIVE_Y",
    ):
        assert base[key] is False

    enabled = _profile(
        custom_simple_human=True,
        custom_fall_recovery=True,
        custom_loot_jitter=True,
        custom_adaptive_y=True,
    )
    assert enabled["CUSTOM_SIMPLE_HUMAN"] is True
    assert enabled["CUSTOM_FALL_RECOVERY"] is True
    assert enabled["CUSTOM_LOOT_JITTER"] is True
    assert enabled["CUSTOM_ADAPTIVE_Y"] is True


def test_loot_jitter_is_true_bypass_when_off(monkeypatch):
    engine, _ = _engine(_profile(custom_loot_jitter=False))

    def should_not_run(*args, **kwargs):
        raise AssertionError("random.uniform must not run while loot jitter is OFF")

    monkeypatch.setattr("nghia_strategy_v10.random.uniform", should_not_run)
    assert engine._loot_delay({"loot_time": 90}) == 90.0


def test_loot_jitter_uses_spotify_09_to_11_window(monkeypatch):
    engine, _ = _engine(_profile(custom_loot_jitter=True))
    seen = {}

    def fake_uniform(low, high):
        seen["range"] = (low, high)
        return 1.1

    monkeypatch.setattr("nghia_strategy_v10.random.uniform", fake_uniform)
    assert engine._loot_delay({"loot_time": 90}) == pytest.approx(99.0)
    assert seen["range"] == (0.9, 1.1)


def test_human_behavior_rest_is_nonblocking_and_off_is_bypass(monkeypatch):
    off_engine, _ = _engine(_profile(custom_simple_human=False))
    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.0)
    assert off_engine._maybe_human_behavior({"jump_key": "SPACE"}, 10.0) is False
    assert off_engine.human_pause_until == 0.0

    on_engine, host = _engine(_profile(custom_simple_human=True))
    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.01)
    monkeypatch.setattr("nghia_strategy_v10.random.uniform", lambda a, b: 4.0)
    assert on_engine._maybe_human_behavior({"jump_key": "SPACE"}, 10.0) is True
    assert on_engine.human_pause_until == pytest.approx(14.0)
    assert host.release_calls >= 1


def test_human_behavior_jump_uses_150_to_300_ms(monkeypatch):
    engine, host = _engine(_profile(custom_simple_human=True))
    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.05)
    monkeypatch.setattr("nghia_strategy_v10.random.randint", lambda a, b: 222)
    assert engine._maybe_human_behavior({"jump_key": "SPACE"}, 10.0) is True
    assert host.behavior_engine.core.semantic_calls[-1] == ("JUMP", "SPACE", 222)


def test_fall_recovery_requires_2_5_seconds_before_action():
    engine, host = _engine(_profile(custom_fall_recovery=True))
    cfg = {"tele_enabled": False, "jump_key": "SPACE"}

    assert engine._fall_recovery_step(cfg, (50, 120), 10.0) is False
    assert engine._fall_recovery_step(cfg, (50, 120), 12.4) is False
    assert host.behavior_engine.core.jump_up_calls == 0
    assert engine._fall_recovery_step(cfg, (50, 120), 12.6) is True
    assert host.behavior_engine.core.jump_up_calls == 1


def test_custom_adaptive_y_is_independent_from_tp_mode(monkeypatch):
    off_engine, _ = _engine(_profile(custom_adaptive_y=False))
    off_calls = []
    off_engine._adaptive_y_step = lambda cfg, pos, now: off_calls.append((pos, now)) or True
    off_engine.tick(
        {"pause_on_focus_loss": False, "auto_loot": False, "spotify_attack_key": ""},
        (50, 100), 1.0,
    )
    assert off_calls == []

    on_engine, _ = _engine(_profile(custom_adaptive_y=True))
    on_calls = []
    on_engine._adaptive_y_step = lambda cfg, pos, now: on_calls.append((pos, now)) or True
    on_engine.tick(
        {"pause_on_focus_loss": False, "auto_loot": False, "spotify_attack_key": ""},
        (50, 100), 1.0,
    )
    assert on_calls == [((50, 100), 1.0)]


def test_custom_map_ui_exposes_four_off_by_default_options_and_persists_them():
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    for token in (
        "SIMPLE Human Behavior",
        "B1/B3 Fall Recovery",
        "Loot Jitter kiểu Spotify",
        "Adaptive Y cho Custom Map",
        "custom_simple_human = tk.BooleanVar(value=False)",
        "custom_fall_recovery = tk.BooleanVar(value=False)",
        "custom_loot_jitter = tk.BooleanVar(value=False)",
        "custom_adaptive_y = tk.BooleanVar(value=False)",
        "custom_simple_human=custom_simple_human.get()",
        "custom_fall_recovery=custom_fall_recovery.get()",
        "custom_loot_jitter=custom_loot_jitter.get()",
        "custom_adaptive_y=custom_adaptive_y.get()",
    ):
        assert token in text


def test_v1009_features_are_still_present():
    ui = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
    controller = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    assert "Hẹn giờ bán MiuMiu" in ui
    assert "client_capture_region(user32, hwnd)" in controller
