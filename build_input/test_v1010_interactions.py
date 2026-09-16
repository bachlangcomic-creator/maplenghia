from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload")).resolve()
sys.path.insert(0, str(APP))


class FakeCore:
    def __init__(self):
        self.jump_up_calls = 0

    def _spotify_jump_up(self, cfg):
        self.jump_up_calls += 1
        return True

    def _spotify_flash_down(self, cfg):
        return True

    def _spotify_jump_down_reconstructed(self, cfg):
        return True

    def _spotify_hold_combo_action(self, *args, **kwargs):
        return True

    def _spotify_input_semantic(self, *args, **kwargs):
        return True


class FakeBehavior:
    def __init__(self):
        self.input_lock = threading.RLock()
        self.core = FakeCore()


class FakeHost:
    def __init__(self):
        self.behavior_engine = FakeBehavior()
        self.running = True
        self.move = None

    def set_move(self, key):
        self.move = key

    def release_move(self):
        self.move = None

    def _input_key_up(self, key):
        return True

    def _game_has_focus(self, cfg):
        return True


def test_adaptive_action_suppresses_same_tick_fall_recovery_action():
    from nghia_strategy_v10 import V10StrategyEngine, build_v10_pirate_profile, resolve_v10_profile

    profile = build_v10_pirate_profile(
        (10, 100), (100, 100), (50, 100),
        (10, 120), (100, 120), (35, 120), (75, 120),
        "SPOTIFY_COMBO", "NONE", "PIRATE_BOTTOM_CUSTOM", 0.6,
        custom_fall_recovery=True,
        custom_adaptive_y=True,
    )
    host = FakeHost()
    engine = V10StrategyEngine(host)
    engine.profile = dict(profile)
    engine.resolved = resolve_v10_profile(profile)
    engine.running = True
    engine.adaptive_y_anchor = 100.0
    engine.next_adaptive_action_at = 0.0
    engine.fall_off_since = 0.0
    engine.next_fall_recovery_at = 0.0

    engine.tick(
        {
            "pause_on_focus_loss": False,
            "auto_loot": False,
            "spotify_attack_key": "",
            "jump_key": "SPACE",
            "tele_enabled": False,
            "left_key": "LEFT",
            "right_key": "RIGHT",
        },
        (50, 120),
        3.0,
    )

    assert host.behavior_engine.core.jump_up_calls == 1
