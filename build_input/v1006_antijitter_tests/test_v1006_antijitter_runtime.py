import sys
from pathlib import Path

APP = (Path(__file__).resolve().parents[1] / 'portable' / 'app_payload').resolve()
sys.path.insert(0, str(APP))

from spotify_recovered_core import SpotifyRecoveredCore


class Host:
    def __init__(self):
        self.map_move_direction = 1
        self.last_map_player_pos = None
        self.last_map_player_seen = 0.0
        self.last_map_missing_log = 0.0
        self.spotify_fall_start_time = 0.0
        self.spotify_r54_fall_kick_done = False
        self.spotify_simple_adaptive_y = None
        self.spotify_edge_side = ''
        self.spotify_edge_departed = True
        self.spotify_edge_lock_until = 0.0
        self.spotify_edge_pause_until = 0.0
        self.spotify_human_pause_until = 0.0
        self.spotify_last_turn_time = 0.0
        self.spotify_scheduler_last_action = ''
        self.spotify_primary_skill_next = 9999.0
        self.spotify_primary_skill_phase = 0
        self.spotify_primary_held_key = None
        self.spotify_pirate_farm_next_attack = 9999.0
        self.spotify_bunny_state = 'TO_B'
        self.spotify_bunny_spam_start = 0.0
        self.spotify_bunny_next_attack = 0.0
        self.spotify_stand_anchor = None
        self.spotify_stand_last_reset = 0.0
        self.spotify_stand_next_reset = 9999.0
        self.spotify_stand_last_turn_dir = 'LEFT'
        self.spotify_stand_last_floor_jump = 0.0
        self.spotify_stand_next_floor_jump = 9999.0
        self.moves = []
        self.logs = []

    def set_move(self, key):
        self.moves.append(('move', key))

    def release_move(self):
        self.moves.append(('release', None))

    def _log(self, message):
        self.logs.append(message)


class CoreUnderTest(SpotifyRecoveredCore):
    def _spotify_update_stuck(self, cfg, map_pos, now):
        return None

    def _spotify_primary_skill_step(self, cfg, now):
        return False

    def _spotify_primary_skill_release(self):
        return None

    def _spotify_hold_combo_action(self, *args, **kwargs):
        return True

    def _spotify_hold_action_legacy(self, *args, **kwargs):
        return True

    def _spotify_input_semantic(self, *args, **kwargs):
        return True


def simple_cfg(enabled):
    return {
        'current_map': 'C1',
        'map_profile': {'LEFT_X': 0, 'RIGHT_X': 100, 'LEFT_Y': 50, 'RIGHT_Y': 50},
        'left_key': 'LEFT', 'right_key': 'RIGHT',
        'jump_key': '', 'tele_key': '', 'tele_enabled': False,
        'spotify_attack_key': '',
        'spotify_runtime_parity_mode': True,
        'anti_jitter_enabled': enabled,
    }


def test_simple_off_turns_on_first_edge_sample_like_v1006():
    host = Host(); core = CoreUnderTest(host)
    core._spotify_left_right_step(simple_cfg(False), (96, 50), 1.0)
    assert host.map_move_direction == -1


def test_simple_on_requires_two_edge_samples_then_turns():
    host = Host(); core = CoreUnderTest(host)
    cfg = simple_cfg(True)
    core._spotify_left_right_step(cfg, (96, 50), 1.0)
    assert host.map_move_direction == 1
    core._spotify_left_right_step(cfg, (97, 50), 1.05)
    assert host.map_move_direction == -1


def test_pirate_normal_on_debounces_farm_edge_without_touching_route_state(monkeypatch):
    host = Host(); core = CoreUnderTest(host)
    host.spotify_pirate_state = 'FARM'
    cfg = {
        'map_profile': {'LEFT_X': 10, 'RIGHT_X': 180, 'LEFT_Y': 180, 'RIGHT_Y': 180},
        'left_key': 'LEFT', 'right_key': 'RIGHT', 'jump_key': '',
        'tele_key': '', 'tele_enabled': False, 'spotify_attack_key': '',
        'anti_jitter_enabled': True,
    }
    monkeypatch.setattr('spotify_recovered_core.time.sleep', lambda _s: None)
    core._spotify_pirate_normal_farm_step(cfg, (176, 180), 2.0)
    assert host.map_move_direction == 1
    assert host.spotify_pirate_state == 'FARM'
    core._spotify_pirate_normal_farm_step(cfg, (177, 180), 2.05)
    assert host.map_move_direction == -1
    assert host.spotify_pirate_state == 'FARM'


def test_simple_missing_position_keeps_original_short_grace_direction():
    host = Host(); core = CoreUnderTest(host)
    host.last_map_player_seen = 10.0
    core._spotify_left_right_step(simple_cfg(True), None, 10.2)
    assert ('move', 'RIGHT') in host.moves
