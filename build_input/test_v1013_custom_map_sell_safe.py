from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import threading
import sys

APP = Path(os.environ.get('NGHIA_APP_DIR', 'portable/app_payload')).resolve()


def load_strategy():
    if str(APP) not in sys.path:
        sys.path.insert(0, str(APP))
    path = APP / 'nghia_strategy_v10.py'
    spec = importlib.util.spec_from_file_location('nghia_strategy_v10_under_test', path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DummyCore:
    pass


class DummyBehaviorEngine:
    def __init__(self):
        self.input_lock = threading.RLock()
        self.core = DummyCore()


class DummyLock:
    def __init__(self, locked=False):
        self._locked = bool(locked)

    def locked(self):
        return self._locked


class DummyHost:
    def __init__(self, stage_result='STOP_TICK'):
        self.behavior_engine = DummyBehaviorEngine()
        self.spotify_sell_inflight = False
        self.sell_lock = DummyLock(False)
        self.stage_result = stage_result
        self.stage_calls = []
        self.release_move_calls = 0

    def _game_has_focus(self, cfg):
        return True

    def _spotify_mainfarm_sell_safe_stage(self, cfg, map_pos, now, owner='SUPERVISOR'):
        self.stage_calls.append((cfg, map_pos, now, owner))
        return self.stage_result

    def release_move(self):
        self.release_move_calls += 1

    def _input_key_up(self, key):
        return True


def make_engine(stage_result='STOP_TICK'):
    mod = load_strategy()
    host = DummyHost(stage_result)
    engine = mod.V10StrategyEngine(host)
    profile = {
        'ENGINE_MODE': 'STRATEGY_V10',
        'FARM_TYPE': 'PIRATE_ROUTE',
        'COMBAT_MODE': 'SPOTIFY_COMBO',
        'TP_MODE': 'NONE',
        'LOOT_MODE': 'NONE',
        'LEFT_X': 10, 'LEFT_Y': 20,
        'RIGHT_X': 100, 'RIGHT_Y': 20,
        'SAFE_PLACE_X': 55, 'SAFE_PLACE_Y': 20,
    }
    engine.running = True
    engine.profile = dict(profile)
    engine.resolved = mod.resolve_v10_profile(profile)
    engine.loot_state = 'FARM'
    return mod, host, engine, profile


def test_sell_safe_stage_preempts_custom_map_farm():
    _mod, host, engine, profile = make_engine('STOP_TICK')
    cfg = {
        'pause_on_focus_loss': True,
        'map_profile': dict(profile),
        'auto_sell': True,
        'sell_only_when_full': True,
        'sell_cooldown': 0,
    }

    def farm_must_not_run(*args, **kwargs):
        raise AssertionError('farm ran while SELL_SAFE owned the tick')

    engine._farm_route_step = farm_must_not_run
    assert engine.tick(cfg, (20, 20), 123.0) is True
    assert len(host.stage_calls) == 1
    called_cfg, called_pos, called_now, owner = host.stage_calls[0]
    assert called_cfg['map_profile']['SAFE_PLACE_X'] == 55
    assert called_pos == (20, 20)
    assert called_now == 123.0
    assert owner == 'V10_STRATEGY'


def test_sell_inflight_blocks_custom_map_inputs_and_farm():
    _mod, host, engine, profile = make_engine('CONTINUE')
    host.spotify_sell_inflight = True
    cfg = {
        'pause_on_focus_loss': True,
        'map_profile': dict(profile),
    }

    def farm_must_not_run(*args, **kwargs):
        raise AssertionError('farm ran while MiuMiu seller was inflight')

    engine._farm_route_step = farm_must_not_run
    assert engine.tick(cfg, (20, 20), 124.0) is True
    assert host.release_move_calls >= 1
    assert host.stage_calls == []


def test_sell_lock_blocks_custom_map_until_seller_releases_ui():
    _mod, host, engine, profile = make_engine('CONTINUE')
    host.sell_lock = DummyLock(True)
    cfg = {
        'pause_on_focus_loss': True,
        'map_profile': dict(profile),
    }

    def farm_must_not_run(*args, **kwargs):
        raise AssertionError('farm ran while sell_lock was owned')

    engine._farm_route_step = farm_must_not_run
    assert engine.tick(cfg, (20, 20), 125.0) is True
    assert host.release_move_calls >= 1
    assert host.stage_calls == []
