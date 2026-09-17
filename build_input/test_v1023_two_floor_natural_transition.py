from pathlib import Path
import os
import sys

APP = Path(os.environ.get('NGHIA_APP_DIR', Path(__file__).resolve().parent / 'app_payload')).resolve()
sys.path.insert(0, str(APP))


def make_profile(**kwargs):
    from nghia_strategy_v10 import build_v10_two_floor_profile
    return build_v10_two_floor_profile(
        (10, 100), (90, 100), (10, 60), (90, 60),
        (70, 100), (30, 60), (50, 40),
        loot_mode='NONE', passes_per_floor=1, **kwargs,
    )


class Core:
    def __init__(self):
        self.move_to_calls = 0
        self.combo_calls = 0
        self.vertical_calls = 0
    def _spotify_move_to_step(self, *a, **k):
        self.move_to_calls += 1
        return False
    def _spotify_jump_up(self, cfg):
        self.vertical_calls += 1
        return True
    def _spotify_jump_down_reconstructed(self, cfg):
        self.vertical_calls += 1
        return True
    def _spotify_flash_down(self, cfg):
        self.vertical_calls += 1
        return True
    def _spotify_input_semantic(self, *a, **k): return True
    def _spotify_tap_combo(self, *a, **k): return True
    def _spotify_hold_combo_action(self, *a, **k):
        self.combo_calls += 1
        return True
    def _spotify_reset_move_to_state(self): pass


class Host:
    def __init__(self):
        import threading
        self.core = Core()
        self.behavior_engine = type('BE', (), {'input_lock': threading.RLock(), 'core': self.core})()
        self.running = True
        self.current_move_key = None
        self.move_history = []
        self.sell_lock = type('L', (), {'locked': lambda self: False})()
        self.spotify_sell_inflight = False
    def set_move(self, key):
        self.current_move_key = key
        self.move_history.append(key)
    def release_move(self): self.current_move_key = None
    def _input_key_up(self, key): return True
    def _input_key_down(self, key): return True
    def _game_has_focus(self, cfg): return True
    def _log(self, msg): pass


def make_engine():
    from nghia_strategy_v10 import V10StrategyEngine, resolve_v10_profile
    host = Host()
    engine = V10StrategyEngine(host)
    profile = make_profile()
    engine.profile = profile
    engine.resolved = resolve_v10_profile(profile)
    engine.running = True
    engine.loot_state = 'FARM'
    engine.next_loot_at = 9999.0
    engine.two_floor_floor = 'BOTTOM'
    engine.two_floor_state = 'MOVE_UP_POINT'
    return engine, host


def cfg():
    return {
        'pause_on_focus_loss': False,
        'right_key': 'RIGHT', 'left_key': 'LEFT', 'jump_key': 'C',
        'tele_enabled': True, 'tele_key': 'X',
        'spotify_attack_key': 'A',
        'auto_loot': False,
    }


def test_transition_travel_uses_normal_cadence_and_does_not_own_move_to():
    engine, host = make_engine()
    engine.direction = -1  # intentionally stale; target is to the RIGHT
    consumed = engine._two_floor_route_step(cfg(), (20, 100), 1.0)
    assert consumed is False
    assert engine.direction == 1
    assert host.current_move_key == 'RIGHT'
    assert host.core.move_to_calls == 0


def test_tick_keeps_spotify_combo_running_while_travelling_to_transition_point():
    engine, host = make_engine()
    engine.direction = -1
    engine.next_combat_at = 0.0
    assert engine.tick(cfg(), (20, 100), 1.0) is True
    assert host.current_move_key == 'RIGHT'
    assert host.core.combo_calls == 1
    assert host.core.move_to_calls == 0


def test_edge_that_arms_floor_change_does_not_drop_the_boundary_combat_tick():
    engine, host = make_engine()
    engine.two_floor_state = 'FARM_BOTTOM'
    engine.direction = 1
    engine.two_floor_leg_origin = 'LEFT'
    engine.next_combat_at = 0.0
    assert engine.tick(cfg(), (90, 100), 2.0) is True
    assert engine.two_floor_state == 'MOVE_UP_POINT'
    assert host.core.combo_calls == 1


def test_arrival_still_performs_vertical_action_and_wait_state_is_safety_gated():
    engine, host = make_engine()
    consumed = engine._two_floor_route_step(cfg(), (70, 100), 3.0)
    assert consumed is True
    assert engine.two_floor_state == 'WAIT_TOP'
    assert host.core.vertical_calls == 1

    combo_before = host.core.combo_calls
    assert engine.tick(cfg(), (70, 90), 3.2) is True
    assert host.core.combo_calls == combo_before
