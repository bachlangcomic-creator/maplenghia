from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

import pytest

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload")).resolve()
sys.path.insert(0, str(APP))


def _profile(enabled=True):
    from nghia_strategy_v10 import build_v10_pirate_profile

    return build_v10_pirate_profile(
        (10, 100), (100, 100), (50, 100),
        (10, 120), (100, 120), (35, 120), (75, 120),
        "SPOTIFY_COMBO", "NONE", "PIRATE_BOTTOM_CUSTOM", 0.6,
        custom_simple_human=enabled,
    )


class FakeCore:
    def __init__(self):
        self.semantic_calls = []

    def _spotify_input_semantic(self, cfg, role, key, hold_ms=0):
        self.semantic_calls.append((role, key, hold_ms))
        return True


class FakeBehavior:
    def __init__(self):
        self.input_lock = threading.RLock()
        self.core = FakeCore()


class FakeHost:
    def __init__(self):
        self.behavior_engine = FakeBehavior()
        self.release_calls = 0

    def release_move(self):
        self.release_calls += 1

    def _input_key_up(self, key):
        return True


def _engine(enabled=True):
    from nghia_strategy_v10 import V10StrategyEngine, resolve_v10_profile

    host = FakeHost()
    engine = V10StrategyEngine(host)
    profile = _profile(enabled)
    engine.profile = dict(profile)
    engine.resolved = resolve_v10_profile(profile)
    engine.running = True
    return engine, host


def test_rest_uses_1000_to_1500_ms_and_stays_nonblocking(monkeypatch):
    engine, host = _engine()
    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.01)
    seen = {}

    def fake_randint(low, high):
        seen["range"] = (low, high)
        return 1250

    monkeypatch.setattr("nghia_strategy_v10.random.randint", fake_randint)
    assert engine._maybe_human_behavior({"jump_key": "SPACE"}, 10.0) is True
    assert seen["range"] == (1000, 1500)
    assert engine.human_pause_until == pytest.approx(11.25)
    assert host.release_calls >= 1


def test_next_six_percent_still_jumps_for_150_to_300_ms(monkeypatch):
    engine, host = _engine()
    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.05)
    seen = {}

    def fake_randint(low, high):
        seen["range"] = (low, high)
        return 222

    monkeypatch.setattr("nghia_strategy_v10.random.randint", fake_randint)
    assert engine._maybe_human_behavior({"jump_key": "SPACE"}, 10.0) is True
    assert seen["range"] == (150, 300)
    assert host.behavior_engine.core.semantic_calls[-1] == ("JUMP", "SPACE", 222)


def test_probability_boundaries_are_2_rest_6_jump_92_continue(monkeypatch):
    engine, host = _engine()
    monkeypatch.setattr("nghia_strategy_v10.random.randint", lambda low, high: 1000 if (low, high) == (1000, 1500) else 150)

    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.019999)
    assert engine._maybe_human_behavior({"jump_key": "SPACE"}, 20.0) is True
    assert engine.human_pause_until == pytest.approx(21.0)

    engine.human_pause_until = 0.0
    host.behavior_engine.core.semantic_calls.clear()
    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.02)
    assert engine._maybe_human_behavior({"jump_key": "SPACE"}, 30.0) is True
    assert host.behavior_engine.core.semantic_calls[-1][0] == "JUMP"

    host.behavior_engine.core.semantic_calls.clear()
    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.079999)
    assert engine._maybe_human_behavior({"jump_key": "SPACE"}, 40.0) is True
    assert host.behavior_engine.core.semantic_calls[-1][0] == "JUMP"

    host.behavior_engine.core.semantic_calls.clear()
    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.08)
    assert engine._maybe_human_behavior({"jump_key": "SPACE"}, 50.0) is False
    assert host.behavior_engine.core.semantic_calls == []


def test_simple_human_off_remains_true_bypass(monkeypatch):
    engine, host = _engine(enabled=False)
    monkeypatch.setattr("nghia_strategy_v10.random.random", lambda: 0.0)

    def should_not_randint(*args, **kwargs):
        raise AssertionError("randint must not run while SIMPLE Human Behavior is OFF")

    monkeypatch.setattr("nghia_strategy_v10.random.randint", should_not_randint)
    assert engine._maybe_human_behavior({"jump_key": "SPACE"}, 10.0) is False
    assert engine.human_pause_until == 0.0
    assert host.release_calls == 0
    assert host.behavior_engine.core.semantic_calls == []


def test_old_three_to_five_second_rest_is_removed():
    text = (APP / "nghia_strategy_v10.py").read_text(encoding="utf-8")
    assert "random.uniform(3.0, 5.0)" not in text
    assert "random.randint(1000, 1500)" in text
