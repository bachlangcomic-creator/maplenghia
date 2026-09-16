from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

import pytest

APP = Path(os.environ.get('NGHIA_APP_DIR', 'portable/app_payload')).resolve()
sys.path.insert(0, str(APP))


def _profile(*, safe_entry=(45, 90), farm_return=(55, 80), fall=True):
    from nghia_strategy_v10 import build_v10_pirate_profile
    return build_v10_pirate_profile(
        (10, 100), (100, 100), (50, 70),
        None, None, None, None,
        'SPOTIFY_COMBO', 'NONE', 'SIMPLE', 0.6,
        custom_fall_recovery=fall,
        safe_entry=safe_entry,
        farm_return=farm_return,
    )


class FakeCore:
    def __init__(self):
        self.up_calls = 0
        self.down_calls = 0
        self.reset_safe_calls = 0
        self.combat_calls = 0

    def _spotify_jump_up(self, cfg):
        self.up_calls += 1
        return True

    def _spotify_jump_down_reconstructed(self, cfg):
        self.down_calls += 1
        return True

    def _spotify_reset_safe_place_state(self):
        self.reset_safe_calls += 1

    def _spotify_input_semantic(self, *args, **kwargs):
        return True

    def _spotify_hold_combo_action(self, *args, **kwargs):
        self.combat_calls += 1
        return True


class FakeBehavior:
    def __init__(self):
        self.input_lock = threading.RLock()
        self.core = FakeCore()
        self.safe_outcomes = []
        self.safe_targets = []

    def safe_place_step(self, cfg, map_pos, now):
        p = cfg.get('map_profile') or {}
        self.safe_targets.append((p.get('SAFE_PLACE_X'), p.get('SAFE_PLACE_Y')))
        return self.safe_outcomes.pop(0) if self.safe_outcomes else 'PENDING'


class FakeHost:
    def __init__(self):
        self.behavior_engine = FakeBehavior()
        self.release_calls = 0
        self.moves = []
        self.spotify_sell_inflight = False
        self.sell_lock = threading.Lock()
        self.running = True

    def release_move(self):
        self.release_calls += 1

    def set_move(self, key):
        self.moves.append(key)

    def _input_key_up(self, key):
        return True


def _engine(profile):
    from nghia_strategy_v10 import V10StrategyEngine, resolve_v10_profile
    host = FakeHost()
    engine = V10StrategyEngine(host)
    engine.profile = dict(profile)
    engine.resolved = resolve_v10_profile(profile)
    engine.running = True
    engine.cfg = {'map_profile': dict(profile)}
    return engine, host


def test_profile_preserves_optional_safe_entry_and_farm_return():
    from nghia_strategy_v10 import resolve_v10_profile
    p = _profile()
    assert p['SAFE_ENTRY_X'] == 45 and p['SAFE_ENTRY_Y'] == 90
    assert p['FARM_RETURN_X'] == 55 and p['FARM_RETURN_Y'] == 80
    r = resolve_v10_profile(p)
    assert r.safe_entry == (45.0, 90.0)
    assert r.farm_return == (55.0, 80.0)


def test_safe_entry_arrival_performs_up_jump_before_real_safe():
    engine, host = _engine(_profile())
    host.behavior_engine.safe_outcomes = ['READY']
    out = engine._custom_sell_entry_step({'map_profile': dict(engine.profile), 'jump_key': 'SPACE'}, (45, 90), 10.0)
    assert out == 'PENDING'
    assert host.behavior_engine.safe_targets[-1] == (45, 90)
    assert host.behavior_engine.core.up_calls == 1
    assert host.behavior_engine.core.reset_safe_calls >= 1
    out2 = engine._custom_sell_entry_step({'map_profile': dict(engine.profile), 'jump_key': 'SPACE'}, (45, 80), 10.6)
    assert out2 == 'READY'


def test_post_sell_return_uses_down_jump_and_waits_for_farm_lane():
    engine, host = _engine(_profile())
    engine.request_post_sell_return()
    cfg = {'jump_key': 'SPACE', 'left_key': 'LEFT', 'right_key': 'RIGHT'}
    assert engine._custom_farm_return_step(cfg, (55, 80), 20.0) is True
    assert host.behavior_engine.core.down_calls == 1
    assert engine.post_sell_return_pending is True
    assert engine._custom_farm_return_step(cfg, (55, 100), 20.7) is False
    assert engine.post_sell_return_pending is False


def test_wrong_upper_floor_activates_farm_return_after_confirm_window():
    engine, host = _engine(_profile(fall=True))
    cfg = {'jump_key': 'SPACE', 'left_key': 'LEFT', 'right_key': 'RIGHT'}
    assert engine._fall_recovery_step(cfg, (60, 80), 30.0) is False
    assert engine._fall_recovery_step(cfg, (60, 80), 32.6) is True
    assert engine.farm_return_active is True


def test_v1016_custom_fields_are_absent_by_default_and_do_not_change_old_profiles():
    from nghia_strategy_v10 import build_v10_pirate_profile, resolve_v10_profile
    p = build_v10_pirate_profile(
        (10, 100), (100, 100), (50, 70),
        None, None, None, None,
        'SPOTIFY_COMBO', 'NONE', 'SIMPLE', 0.6,
    )
    assert 'SAFE_ENTRY_X' not in p and 'FARM_RETURN_X' not in p
    r = resolve_v10_profile(p)
    assert r.safe_entry is None and r.farm_return is None


def test_custom_map_builder_exposes_five_farm_coordinate_slots():
    text = (APP / 'maple_nghia_pro.py').read_text(encoding='utf-8')
    assert '"SAFE_ENTRY": "SAFE ENTRY"' in text
    assert '"FARM_RETURN": "FARM RETURN"' in text
    assert '("LEFT", "RIGHT", "SAFE_ENTRY", "SAFE", "FARM_RETURN")' in text


def test_sell_worker_requests_return_only_for_v10_custom_profile():
    text = (APP / 'maple_nghia_pro.py').read_text(encoding='utf-8')
    assert 'request_post_sell_return' in text
    assert 'SAFE_ENTRY_X' in text and 'FARM_RETURN_X' in text


def test_tick_does_not_combat_while_farm_return_owns_recovery():
    engine, host = _engine(_profile(fall=True))
    engine.fall_off_since = 30.0
    cfg = {
        'jump_key': 'SPACE', 'left_key': 'LEFT', 'right_key': 'RIGHT',
        'spotify_attack_key': 'X', 'tele_enabled': False, 'auto_loot': False,
        'pause_on_focus_loss': False,
    }
    assert engine.tick(cfg, (60, 80), 32.6) is True
    assert engine.farm_return_active is True
    assert host.behavior_engine.core.combat_calls == 0
