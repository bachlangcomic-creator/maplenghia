"""Public adapter for the behavior recovered from the Spotify/Mage Farmer binary.

The original program exposed route and movement helpers as free functions.  Nghĩa
keeps the recovered state machines in ``SpotifyRecoveredCore``; this adapter gives
those behaviors a small, stable API without coupling callers to private method
names on the core.
"""


class SpotifyRecoveredAPI:
    """Expose the recovered Spotify function inventory through one object."""

    def __init__(self, core):
        self.core = core

    def hold_combo_action(self, cfg, direction_key, flash_key, skill_key, hold_time):
        return self.core._spotify_hold_combo_action(
            cfg, direction_key, flash_key, skill_key, hold_time)

    def left_flash(self, cfg, hold_time=None):
        return self.core._spotify_left_flash(cfg, hold_time=hold_time)

    def right_flash(self, cfg, hold_time=None):
        return self.core._spotify_right_flash(cfg, hold_time=hold_time)

    def left_jump(self, cfg, hold_time=None):
        return self.core._spotify_left_jump(cfg, hold_time=hold_time)

    def right_jump(self, cfg, hold_time=None):
        return self.core._spotify_right_jump(cfg, hold_time=hold_time)

    def move_and_jump(self, cfg, direction_key, action_ms=None):
        return self.core._spotify_move_and_jump_reconstructed(
            cfg, direction_key, action_ms=action_ms)

    def random_move(self, cfg, cycles=2):
        return self.core._spotify_random_move_reconstructed(cfg, cycles=cycles)

    def flash_down(self, cfg, hold_time=None):
        return self.core._spotify_flash_down(cfg, hold_time=hold_time)

    def jump_down(self, cfg):
        return self.core._spotify_jump_down_reconstructed(cfg)

    def perform_dynamic_combo(self, cfg, combo_type, direction_key, *, hold_ms=None):
        return self.core._spotify_dynamic_combo_reconstructed(
            cfg, combo_type, direction_key, hold_ms=hold_ms)

    def run_left_and_right(self, cfg, map_pos, now):
        return self.core._spotify_left_right_step(cfg, map_pos, now)

    def run_stand_still(self, cfg, map_pos, now):
        return self.core._spotify_stand_still_step(cfg, map_pos, now)

    def run_bunny(self, cfg, map_pos, now):
        return self.core._spotify_bunny_step(cfg, map_pos, now)

    def run_pirate2(self, cfg, map_pos, now):
        return self.core._spotify_pirate_step(cfg, map_pos, now, one_hit=False)

    def run_pirate2_1hit(self, cfg, map_pos, now):
        return self.core._spotify_pirate_step(cfg, map_pos, now, one_hit=True)

    def dispatch(self, profile_kind, cfg, map_pos, now):
        kind = str(profile_kind or "NONE").upper()
        routes = {
            "LEFT_RIGHT": self.run_left_and_right,
            "STAND_STILL": self.run_stand_still,
            "BUNNY": self.run_bunny,
            "PIRATE2": self.run_pirate2,
            "PIRATE2_1HIT": self.run_pirate2_1hit,
        }
        route = routes.get(kind)
        if route is None:
            return False
        return route(cfg, map_pos, now)
