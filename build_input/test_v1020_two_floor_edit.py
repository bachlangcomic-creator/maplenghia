from pathlib import Path
import json
import os
import sys

APP = Path(os.environ.get('NGHIA_APP_DIR', Path(__file__).resolve().parent / 'app_payload')).resolve()
sys.path.insert(0, str(APP))


def test_two_floor_profile_round_trip():
    from nghia_strategy_v10 import build_v10_two_floor_profile, resolve_v10_profile
    profile = build_v10_two_floor_profile(
        bottom_left=(10, 100), bottom_right=(90, 100),
        top_left=(12, 60), top_right=(88, 60),
        up_point=(85, 100), down_point=(15, 60), safe=(50, 40),
        combat_mode='SPOTIFY_COMBO', tp_mode='SPAM_TP_SKILL', loot_mode='SIMPLE',
        up_mode='JUMP_UP', down_mode='DOWN_JUMP',
        two_floor_adaptive_y=True, two_floor_recovery=True,
        change_each_leg=True, safe_entry=(48, 42),
    )
    assert profile['ENGINE_MODE'] == 'STRATEGY_V10'
    assert profile['FARM_TYPE'] == 'TWO_FLOOR_ROUTE'
    assert profile['BOTTOM_LEFT_X'] == 10
    assert profile['TOP_RIGHT_Y'] == 60
    assert profile['UP_POINT_X'] == 85
    assert profile['DOWN_POINT_Y'] == 60
    assert profile['TWO_FLOOR_UP_MODE'] == 'JUMP_UP'
    assert profile['TWO_FLOOR_DOWN_MODE'] == 'DOWN_JUMP'
    assert profile['TWO_FLOOR_ADAPTIVE_Y'] is True
    assert profile['TWO_FLOOR_RECOVERY'] is True
    assert profile['TWO_FLOOR_CHANGE_EACH_LEG'] is True
    resolved = resolve_v10_profile(profile)
    assert resolved.farm_type == 'TWO_FLOOR_ROUTE'
    assert resolved.bottom_left == (10.0, 100.0)
    assert resolved.top_right == (88.0, 60.0)
    assert resolved.up_point == (85.0, 100.0)
    assert resolved.down_point == (15.0, 60.0)


def test_two_floor_rejects_pirate_bottom_custom():
    import pytest
    from nghia_strategy_v10 import build_v10_two_floor_profile, V10ProfileError
    with pytest.raises(V10ProfileError):
        build_v10_two_floor_profile(
            (10,100),(90,100),(10,60),(90,60),(90,100),(10,60),(50,40),
            loot_mode='PIRATE_BOTTOM_CUSTOM'
        )


def test_two_floor_state_changes_floor_only_after_verified_y():
    from nghia_strategy_v10 import build_v10_two_floor_profile, V10StrategyEngine

    class Core:
        def __init__(self):
            self.up_calls = 0
        def _spotify_move_to_step(self, cfg, pos, x, y, now, **kwargs):
            return abs(pos[0]-x) <= 2 and abs(pos[1]-y) <= 4
        def _spotify_jump_up(self, cfg):
            self.up_calls += 1
            return True
        def _spotify_jump_down_reconstructed(self, cfg):
            return True
        def _spotify_flash_down(self, cfg):
            return True
        def _spotify_input_semantic(self, *a, **k):
            return True
        def _spotify_tap_combo(self, *a, **k):
            return True
        def _spotify_hold_combo_action(self, *a, **k):
            return True
        def _spotify_reset_move_to_state(self):
            pass

    class Host:
        def __init__(self):
            import threading
            self.behavior_engine = type('BE', (), {'input_lock': threading.RLock(), 'core': Core()})()
            self.running = True
            self.moves = []
            self.current_move_key = None
            self.sell_lock = type('L', (), {'locked': lambda self: False})()
            self.spotify_sell_inflight = False
        def set_move(self, key):
            self.current_move_key = key
            self.moves.append(key)
        def release_move(self):
            self.current_move_key = None
        def _input_key_up(self, key):
            return True
        def _input_key_down(self, key):
            return True
        def _game_has_focus(self, cfg):
            return True
        def _log(self, msg):
            pass

    host = Host()
    engine = V10StrategyEngine(host)
    profile = build_v10_two_floor_profile(
        (10,100),(90,100),(10,60),(90,60),(90,100),(10,60),(50,40),
        loot_mode='NONE', change_each_leg=True,
    )
    engine.resolved = __import__('nghia_strategy_v10').resolve_v10_profile(profile)
    engine.profile = profile
    engine.running = True
    engine.two_floor_state = 'FARM_BOTTOM'
    engine.direction = 1
    engine.two_floor_floor = 'BOTTOM'

    # Reaching the bottom-right edge should request a floor transition, not instantly claim TOP.
    acted = engine._two_floor_route_step({'right_key':'RIGHT','left_key':'LEFT','jump_key':'C'}, (90,100), 10.0)
    assert acted is True
    assert engine.two_floor_state == 'MOVE_UP_POINT'
    assert engine.two_floor_floor == 'BOTTOM'

    # At UP_POINT, action is sent, but floor remains BOTTOM until Y is verified near top lane.
    engine._two_floor_route_step({'right_key':'RIGHT','left_key':'LEFT','jump_key':'C'}, (90,100), 10.1)
    assert engine.two_floor_state == 'WAIT_TOP'
    assert engine.two_floor_floor == 'BOTTOM'
    assert host.behavior_engine.core.up_calls == 1

    engine._two_floor_route_step({'right_key':'RIGHT','left_key':'LEFT','jump_key':'C'}, (90,85), 10.4)
    assert engine.two_floor_floor == 'BOTTOM'

    engine._two_floor_route_step({'right_key':'RIGHT','left_key':'LEFT','jump_key':'C'}, (88,61), 10.6)
    assert engine.two_floor_floor == 'TOP'
    assert engine.two_floor_state == 'FARM_TOP'


def test_replace_map_profile_renames_without_duplicate(tmp_path):
    from nghia_custom_map_profiles import replace_map_profile
    target = tmp_path / 'maps.json'
    maps = {'Old': {'FARM_TYPE':'SIMPLE'}, 'Other': {'FARM_TYPE':'SIMPLE'}}
    updated = replace_map_profile(target, maps, 'Old', 'Renamed', {'FARM_TYPE':'TWO_FLOOR_ROUTE'})
    assert 'Old' not in updated
    assert updated['Renamed']['FARM_TYPE'] == 'TWO_FLOOR_ROUTE'
    assert updated['Other']['FARM_TYPE'] == 'SIMPLE'
    assert json.loads(target.read_text(encoding='utf-8')) == updated


def test_builder_state_loads_two_floor_profile():
    from nghia_custom_map_profiles import profile_to_builder_state
    profile = {
        'ENGINE_MODE':'STRATEGY_V10','FARM_TYPE':'TWO_FLOOR_ROUTE',
        'BOTTOM_LEFT_X':10,'BOTTOM_LEFT_Y':100,'BOTTOM_RIGHT_X':90,'BOTTOM_RIGHT_Y':100,
        'TOP_LEFT_X':12,'TOP_LEFT_Y':60,'TOP_RIGHT_X':88,'TOP_RIGHT_Y':60,
        'UP_POINT_X':85,'UP_POINT_Y':100,'DOWN_POINT_X':15,'DOWN_POINT_Y':60,
        'SAFE_PLACE_X':50,'SAFE_PLACE_Y':40,'SAFE_ENTRY_X':48,'SAFE_ENTRY_Y':42,
        'COMBAT_MODE':'SPOTIFY_COMBO','TP_MODE':'SPAM_TP_SKILL','LOOT_MODE':'SIMPLE',
        'TWO_FLOOR_UP_MODE':'JUMP_UP','TWO_FLOOR_DOWN_MODE':'DOWN_JUMP',
        'TWO_FLOOR_ADAPTIVE_Y':True,'TWO_FLOOR_RECOVERY':True,'TWO_FLOOR_CHANGE_EACH_LEG':True,
    }
    state = profile_to_builder_state(profile)
    assert state['map_type'] == 'TWO FLOOR ROUTE'
    assert state['captured']['BOTTOM_LEFT'] == (10,100)
    assert state['captured']['TOP_RIGHT'] == (88,60)
    assert state['captured']['UP_POINT'] == (85,100)
    assert state['captured']['SAFE_ENTRY'] == (48,42)
    assert state['up_mode'] == 'JUMP_UP'
    assert state['two_floor_recovery'] is True
