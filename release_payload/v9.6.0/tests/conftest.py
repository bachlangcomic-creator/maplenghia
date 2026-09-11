from types import SimpleNamespace
import pytest


class FakeHost(SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.events = []
        self.current_move_key = None
        self.map_move_direction = 1
        self.spotify_primary_held_key = None
        self.spotify_primary_skill_next = 0.0
        self.spotify_primary_skill_phase = 0
        self.spotify_primary_last_action = 0.0
        self.spotify_aux_last_action = 0.0
        self.spotify_scheduler_last_action = ""
        self.spotify_edge_lock_until = 0.0
        self.spotify_edge_side = ""
        self.spotify_edge_departed = True
        self.spotify_edge_pause_until = 0.0
        self.spotify_human_pause_until = 0.0
        self.spotify_recovery_pause_until = 0.0
        self.spotify_recovery_stage = 0
        self.spotify_bunny_state = "TO_B"
        self.spotify_bunny_spam_start = 0.0
        self.spotify_bunny_next_attack = 0.0
        self.spotify_stand_anchor = None
        self.spotify_stand_last_reset = 0.0
        self.spotify_stand_next_reset = 20
        self.spotify_stand_last_turn_dir = "RIGHT"
        self.spotify_stand_last_floor_jump = 0.0
        self.spotify_stand_next_floor_jump = 9999.0
        self.spotify_pirate_state = "FARM"
        self.spotify_pirate_top_substate = "MOVE_TOP"
        self.spotify_pirate_top_direction = 1
        self.spotify_pirate_loot_substate = "TO_START"
        self.spotify_pirate_phase_started = 0.0
        self.spotify_pirate_onehit_state = "MOVE"
        self.spotify_pirate_onehit_wait_until = 0.0
        self.spotify_pirate_onehit_attacked = False
        self.spotify_pirate_loot_dir = 1
        self.spotify_pirate_last_loot = 0.0
        self.spotify_pirate_next_loot = 9999.0
        self.spotify_pirate_last_toploot = 0.0
        self.spotify_pirate_next_toploot = 9999.0
        self.spotify_pirate_loot_defer_until = 0.0
        self.spotify_pirate_farm_next_attack = 0.0
        self.spotify_pirate_sweep_combo_done = False
        self.spotify_r54_pirate_sweep_burst_done = False
        self.spotify_pirate_next_loot_tap = 0.0
        self.spotify_pirate_casted_this_leg = False
        self.spotify_pirate_last_farm_pos = None
        self.spotify_pirate_last_farm_pos_time = 0.0
        self.spotify_pirate_last_farm_direction = 0
        self.spotify_fall_start_time = 0.0
        self.spotify_recovery_reason = ""
        self.spotify_recovery_route_memory = None
        self.spotify_r54_safe_arrived_at = 0.0
        self.last_map_player_seen = 0.0
        self.last_map_player_pos = None
        self.last_map_missing_log = 0.0
        self.last_tele_time = 0.0
        self.auto_pet = False

    def __getattr__(self, name):
        if name.startswith("spotify_") or name.startswith("last_"):
            return 0
        raise AttributeError(name)

    def _spotify_profile_kind(self, cfg):
        return cfg.get("kind", cfg.get("farm_type", "NONE"))

    def _focus_game(self, cfg):
        self.events.append(("cached_focus",))
        return True

    def _game_has_focus(self, cfg):
        self.events.append(("cached_focus",))
        return True

    def _spotify_cached_game_has_focus(self):
        self.events.append(("cached_focus",))
        return True

    def _spotify_focus_refresh(self, cfg, force=True):
        self.events.append(("focus_refresh", bool(force)))
        return True

    def _spotify_cached_game_hwnd(self):
        self.events.append(("cached_hwnd",))
        return 111

    def _find_game_window(self, *_args, **_kwargs):
        raise AssertionError("hot path must not enumerate/find windows")

    def set_move(self, key):
        self.current_move_key = key
        self.events.append(("move", key))
        return True

    def release_move(self):
        if self.current_move_key:
            self.events.append(("move_up", self.current_move_key))
        self.current_move_key = None

    def _press_input_key(self, key, hold_ms=None):
        self.events.append(("press", key, hold_ms))
        return True

    def _input_key_down(self, key):
        self.events.append(("down", key))
        if key:
            self.spotify_primary_held_key = key if key == "A" else self.spotify_primary_held_key
        return True

    def _input_key_up(self, key):
        self.events.append(("up", key))
        if self.spotify_primary_held_key == key:
            self.spotify_primary_held_key = None
        return True

    def _release_all_owned_inputs(self):
        if self.spotify_primary_held_key:
            self._input_key_up(self.spotify_primary_held_key)
        self.release_move()
        self.events.append(("release_all",))

    def _log(self, text):
        self.events.append(("log", text))


@pytest.fixture
def fake_host():
    return FakeHost()
