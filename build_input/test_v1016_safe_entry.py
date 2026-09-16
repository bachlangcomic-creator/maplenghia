from __future__ import annotations

import os
import threading
import types
import unittest
import ctypes

if not hasattr(ctypes, "windll"):
    class _DummyUser32:
        def __getattr__(self, name):
            return lambda *args, **kwargs: 0
    ctypes.windll = types.SimpleNamespace(user32=_DummyUser32())
from pathlib import Path

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload")).resolve()
import sys
sys.path.insert(0, str(APP))

import maple_nghia_pro as pro
from nghia_strategy_v10 import build_v10_pirate_profile


class _Core:
    def __init__(self):
        self.move_calls = []
        self.jump_calls = 0
        self.reset_safe_calls = 0

    def _spotify_move_to_step(self, cfg, map_pos, x, y, now, **kwargs):
        self.move_calls.append((x, y, kwargs))
        return True

    def _spotify_jump_up(self, cfg, hold_time=None):
        self.jump_calls += 1
        return True

    def _spotify_reset_safe_place_state(self):
        self.reset_safe_calls += 1


class _Behavior:
    def __init__(self):
        self.core = _Core()
        self.input_lock = threading.RLock()
        self.safe_calls = 0
        self.safe_result = "READY"
        self.release_calls = 0

    def safe_place_step(self, cfg, map_pos, now):
        self.safe_calls += 1
        return self.safe_result

    def release_inputs(self):
        self.release_calls += 1


class SafeEntryTests(unittest.TestCase):
    def make_app(self):
        app = types.SimpleNamespace()
        app.behavior_engine = _Behavior()
        app.spotify_full_bag_event = threading.Event()
        app.spotify_sell_timer_event = threading.Event()
        app.spotify_sell_inflight = False
        app.last_sell_time = 0.0
        app.sell_lock = threading.Lock()
        app.logs = []
        app.run_sell_calls = 0
        app.pause_add_calls = []
        app._log = app.logs.append
        app._c2_pause_add = app.pause_add_calls.append
        app.run_sell_thread = lambda cfg: setattr(app, "run_sell_calls", app.run_sell_calls + 1)
        app.spotify_r54_safe_state = "MOVE_SAFE"
        if hasattr(pro.MapleNghiaPro, "_spotify_custom_safe_entry_step"):
            app._spotify_custom_safe_entry_step = types.MethodType(pro.MapleNghiaPro._spotify_custom_safe_entry_step, app)
        if hasattr(pro.MapleNghiaPro, "_spotify_reset_custom_safe_entry_state"):
            app._spotify_reset_custom_safe_entry_state = types.MethodType(pro.MapleNghiaPro._spotify_reset_custom_safe_entry_state, app)
        return app

    def test_profile_builders_persist_optional_safe_entry(self):
        simple = pro.build_simple_map_profile((10, 20), (30, 20), (25, 10), safe_entry=(20, 20))
        self.assertEqual((simple["SAFE_ENTRY_X"], simple["SAFE_ENTRY_Y"]), (20, 20))

        pirate = pro.build_pirate_map_profile(
            (10, 20), (30, 20), (25, 10),
            (8, 30), (32, 30), (15, 30), (25, 30),
            safe_entry=(20, 20),
        )
        self.assertEqual((pirate["SAFE_ENTRY_X"], pirate["SAFE_ENTRY_Y"]), (20, 20))

        v10 = build_v10_pirate_profile(
            (10, 20), (30, 20), (25, 10),
            None, None, None, None,
            "SPOTIFY_COMBO", "SPAM_TP_SKILL", "SIMPLE", 0.6,
            safe_entry=(20, 20),
        )
        self.assertEqual((v10["SAFE_ENTRY_X"], v10["SAFE_ENTRY_Y"]), (20, 20))

    def test_profile_builders_keep_safe_entry_optional_for_old_custom_maps(self):
        simple = pro.build_simple_map_profile((10, 20), (30, 20), (25, 10))
        self.assertNotIn("SAFE_ENTRY_X", simple)
        self.assertNotIn("SAFE_ENTRY_Y", simple)

        v10 = build_v10_pirate_profile(
            (10, 20), (30, 20), (25, 10),
            None, None, None, None,
            "SPOTIFY_COMBO", "SPAM_TP_SKILL", "SIMPLE", 0.6,
        )
        self.assertNotIn("SAFE_ENTRY_X", v10)
        self.assertNotIn("SAFE_ENTRY_Y", v10)

    def test_safe_entry_moves_then_up_jumps_then_becomes_ready(self):
        app = self.make_app()
        cfg = {
            "jump_key": "C",
            "map_profile": {
                "SAFE_ENTRY_X": 20,
                "SAFE_ENTRY_Y": 20,
                "SAFE_PLACE_X": 25,
                "SAFE_PLACE_Y": 10,
            },
        }

        self.assertEqual(pro.MapleNghiaPro._spotify_custom_safe_entry_step(app, cfg, (15, 20), 10.0), "PENDING")
        self.assertEqual(len(app.behavior_engine.core.move_calls), 1)
        self.assertEqual(app.behavior_engine.core.jump_calls, 0)

        self.assertEqual(pro.MapleNghiaPro._spotify_custom_safe_entry_step(app, cfg, (20, 20), 10.05), "PENDING")
        self.assertEqual(app.behavior_engine.core.jump_calls, 1)

        self.assertEqual(pro.MapleNghiaPro._spotify_custom_safe_entry_step(app, cfg, (20, 18), 10.40), "READY")
        self.assertEqual(app.behavior_engine.core.jump_calls, 1)

    def test_sell_safe_waits_for_safe_entry_before_existing_safe_place(self):
        app = self.make_app()
        app.spotify_sell_timer_event.set()
        cfg = {
            "auto_sell": True,
            "auto_sell_timer_enabled": True,
            "sell_cooldown": 0,
            "jump_key": "C",
            "map_profile": {
                "SAFE_ENTRY_X": 20,
                "SAFE_ENTRY_Y": 20,
                "SAFE_PLACE_X": 25,
                "SAFE_PLACE_Y": 10,
            },
        }
        app._spotify_custom_safe_entry_step = types.MethodType(
            lambda self, cfg, pos, now: "PENDING", app
        )
        result = pro.MapleNghiaPro._spotify_mainfarm_sell_safe_stage(app, cfg, (15, 20), 100.0, owner="V10_STRATEGY")
        self.assertEqual(result, "STOP_TICK")
        self.assertEqual(app.behavior_engine.safe_calls, 0)
        self.assertEqual(app.run_sell_calls, 0)

        app._spotify_custom_safe_entry_step = types.MethodType(
            lambda self, cfg, pos, now: "READY", app
        )
        result = pro.MapleNghiaPro._spotify_mainfarm_sell_safe_stage(app, cfg, (25, 10), 100.1, owner="V10_STRATEGY")
        self.assertEqual(result, "STOP_TICK")
        self.assertEqual(app.behavior_engine.safe_calls, 1)
        self.assertEqual(app.run_sell_calls, 1)

    def test_builder_ui_has_safe_entry_but_no_farm_return_yet(self):
        text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
        self.assertIn('"SAFE_ENTRY": "SAFE ENTRY"', text)
        self.assertIn('("LEFT", "RIGHT", "SAFE_ENTRY", "SAFE")', text)
        self.assertNotIn("FARM_RETURN", text)
        self.assertNotIn("FARM RETURN", text)

    def test_safe_failure_resets_safe_entry_for_next_sell_attempt(self):
        app = self.make_app()
        app.spotify_sell_timer_event.set()
        app.behavior_engine.safe_result = "FAILED"
        app.spotify_custom_safe_entry_state = "DONE"
        cfg = {
            "auto_sell": True,
            "auto_sell_timer_enabled": True,
            "sell_cooldown": 0,
            "jump_key": "C",
            "map_profile": {
                "SAFE_ENTRY_X": 20,
                "SAFE_ENTRY_Y": 20,
                "SAFE_PLACE_X": 25,
                "SAFE_PLACE_Y": 10,
            },
        }
        result = pro.MapleNghiaPro._spotify_mainfarm_sell_safe_stage(
            app, cfg, (25, 10), 100.0, owner="V10_STRATEGY"
        )
        self.assertEqual(result, "STOP_TICK")
        self.assertEqual(app.spotify_custom_safe_entry_state, "MOVE_ENTRY")

    def test_no_safe_entry_keeps_existing_direct_safe_behavior(self):
        app = self.make_app()
        app.spotify_sell_timer_event.set()
        cfg = {
            "auto_sell": True,
            "auto_sell_timer_enabled": True,
            "sell_cooldown": 0,
            "jump_key": "C",
            "map_profile": {"SAFE_PLACE_X": 25, "SAFE_PLACE_Y": 10},
        }
        result = pro.MapleNghiaPro._spotify_mainfarm_sell_safe_stage(app, cfg, (25, 10), 100.0, owner="V10_STRATEGY")
        self.assertEqual(result, "STOP_TICK")
        self.assertEqual(app.behavior_engine.safe_calls, 1)
        self.assertEqual(app.run_sell_calls, 1)


if __name__ == "__main__":
    unittest.main()
