from pathlib import Path
import os
import sys

APP = Path(os.environ.get('NGHIA_APP_DIR', Path(__file__).resolve().parent / 'app_payload')).resolve()
sys.path.insert(0, str(APP))


def make_profile(**kwargs):
    from nghia_strategy_v10 import build_v10_two_floor_profile
    return build_v10_two_floor_profile(
        (10,100),(90,100),(10,60),(90,60),(90,100),(10,60),(50,40),
        loot_mode='NONE', **kwargs,
    )


def test_two_floor_passes_per_floor_round_trip():
    from nghia_strategy_v10 import resolve_v10_profile
    p = make_profile(passes_per_floor=3)
    assert p['TWO_FLOOR_PASSES_PER_FLOOR'] == 3
    resolved = resolve_v10_profile(p)
    assert resolved.two_floor_passes_per_floor == 3


def test_two_floor_passes_per_floor_validates_1_to_10():
    import pytest
    from nghia_strategy_v10 import V10ProfileError
    with pytest.raises(V10ProfileError):
        make_profile(passes_per_floor=0)
    with pytest.raises(V10ProfileError):
        make_profile(passes_per_floor=11)


def test_first_edge_arms_route_and_only_full_crossings_count():
    from nghia_strategy_v10 import V10StrategyEngine, resolve_v10_profile

    class Core:
        def _spotify_move_to_step(self, *a, **k): return False
        def _spotify_jump_up(self, cfg): return True
        def _spotify_jump_down_reconstructed(self, cfg): return True
        def _spotify_flash_down(self, cfg): return True
        def _spotify_input_semantic(self, *a, **k): return True
        def _spotify_tap_combo(self, *a, **k): return True
        def _spotify_hold_combo_action(self, *a, **k): return True
        def _spotify_reset_move_to_state(self): pass

    class Host:
        def __init__(self):
            import threading
            self.behavior_engine = type('BE', (), {'input_lock': threading.RLock(), 'core': Core()})()
            self.running = True
            self.current_move_key = None
            self.sell_lock = type('L', (), {'locked': lambda self: False})()
            self.spotify_sell_inflight = False
        def set_move(self, key): self.current_move_key = key
        def release_move(self): self.current_move_key = None
        def _input_key_up(self, key): return True
        def _input_key_down(self, key): return True
        def _game_has_focus(self, cfg): return True
        def _log(self, msg): pass

    engine = V10StrategyEngine(Host())
    p = make_profile(passes_per_floor=2)
    engine.profile = p
    engine.resolved = resolve_v10_profile(p)
    engine.running = True
    engine.two_floor_state = 'FARM_BOTTOM'
    engine.two_floor_floor = 'BOTTOM'
    engine.direction = 1

    cfg = {'right_key':'RIGHT','left_key':'LEFT','jump_key':'C'}

    # Merely touching the first edge after START establishes the origin; it is not a completed pass.
    engine._two_floor_route_step(cfg, (90,100), 1.0)
    assert engine.two_floor_state == 'FARM_BOTTOM'
    assert engine.two_floor_passes == 0
    assert engine.two_floor_leg_origin == 'RIGHT'

    # RIGHT -> LEFT is pass #1, still same floor because 2 passes are required.
    engine._two_floor_route_step(cfg, (10,100), 2.0)
    assert engine.two_floor_state == 'FARM_BOTTOM'
    assert engine.two_floor_passes == 1
    assert engine.two_floor_leg_origin == 'LEFT'

    # LEFT -> RIGHT is pass #2, now request the floor transition.
    engine._two_floor_route_step(cfg, (90,100), 3.0)
    assert engine.two_floor_state == 'MOVE_UP_POINT'
    assert engine.two_floor_passes == 0


def test_builder_state_preserves_pass_count_and_legacy_fallback():
    from nghia_custom_map_profiles import profile_to_builder_state
    base = {
        'ENGINE_MODE':'STRATEGY_V10','FARM_TYPE':'TWO_FLOOR_ROUTE',
        'TWO_FLOOR_PASSES_PER_FLOOR':4,
    }
    assert profile_to_builder_state(base)['passes_per_floor'] == 4

    legacy = {
        'ENGINE_MODE':'STRATEGY_V10','FARM_TYPE':'TWO_FLOOR_ROUTE',
        'TWO_FLOOR_CHANGE_EACH_LEG':False,
    }
    assert profile_to_builder_state(legacy)['passes_per_floor'] == 2
