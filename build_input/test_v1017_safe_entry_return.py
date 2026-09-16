from __future__ import annotations

import ctypes
import os
from pathlib import Path
import sys
import threading
import types
import unittest

if not hasattr(ctypes, "windll"):
    class _DummyUser32:
        def __getattr__(self, name):
            return lambda *args, **kwargs: 0
    ctypes.windll = types.SimpleNamespace(user32=_DummyUser32())

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload")).resolve()
sys.path.insert(0, str(APP))

import maple_nghia_pro as pro
from nghia_strategy_v10 import V10StrategyEngine, build_v10_pirate_profile, resolve_v10_profile


class _Core:
    def __init__(self):
        self.move_calls = []
        self.jump_calls = 0
        self.down_jump_calls = 0
        self.reset_safe_calls = 0
        self.combat_calls = 0

    def _spotify_move_to_step(self, cfg, map_pos, x, y, now, **kwargs):
        self.move_calls.append((x, y, kwargs))
        return True

    def _spotify_jump_up(self, cfg, hold_time=None):
        self.jump_calls += 1
        return True

    def _spotify_jump_down_reconstructed(self, cfg):
        self.down_jump_calls += 1
        return True

    def _spotify_reset_safe_place_state(self):
        self.reset_safe_calls += 1

    def _spotify_input_semantic(self, *args, **kwargs):
        return True

    def _spotify_hold_combo_action(self, *args, **kwargs):
        self.combat_calls += 1
        return True


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


class _Host:
    def __init__(self):
        self.behavior_engine = _Behavior()
        self.spotify_full_bag_event = threading.Event()
        self.spotify_sell_timer_event = threading.Event()
        self.spotify_sell_inflight = False
        self.last_sell_time = 0.0
        self.sell_lock = threading.Lock()
        self.logs = []
        self.run_sell_calls = 0
        self.pause_add_calls = []
        self.moves = []
        self.release_calls = 0
        self.running = True
        self._log = self.logs.append
        self._c2_pause_add = self.pause_add_calls.append
        self.run_sell_thread = lambda cfg: setattr(self, "run_sell_calls", self.run_sell_calls + 1)
        self.spotify_r54_safe_state = "MOVE_SAFE"

    def release_move(self):
        self.release_calls += 1

    def set_move(self, key):
        self.moves.append(key)

    def _input_key_up(self, key):
        return True

    def _input_key_down(self, key):
        return True


def _v10_profile(*, safe_entry=(20, 20)):
    return build_v10_pirate_profile(
        (10, 20), (30, 20), (25, 10),
        None, None, None, None,
        "SPOTIFY_COMBO", "NONE", "SIMPLE", 0.6,
        safe_entry=safe_entry,
    )


def _strategy(*, safe_entry=(20, 20)):
    host = _Host()
    profile = _v10_profile(safe_entry=safe_entry)
    engine = V10StrategyEngine(host)
    engine.profile = dict(profile)
    engine.resolved = resolve_v10_profile(profile)
    engine.running = True
    engine.cfg = {"map_profile": dict(profile)}
    host.strategy_v10 = engine
    return engine, host


class SafeEntryReturnTests(unittest.TestCase):
    def make_app(self):
        app = _Host()
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
        v10 = _v10_profile(safe_entry=(20, 20))
        self.assertEqual((v10["SAFE_ENTRY_X"], v10["SAFE_ENTRY_Y"]), (20, 20))

    def test_profile_builders_keep_safe_entry_optional_for_old_custom_maps(self):
        simple = pro.build_simple_map_profile((10, 20), (30, 20), (25, 10))
        self.assertNotIn("SAFE_ENTRY_X", simple)
        v10 = _v10_profile(safe_entry=None)
        self.assertNotIn("SAFE_ENTRY_X", v10)
        self.assertNotIn("SAFE_ENTRY_Y", v10)

    def test_safe_entry_moves_then_up_jumps_then_becomes_ready(self):
        app = self.make_app()
        cfg = {"jump_key": "C", "map_profile": {"SAFE_ENTRY_X": 20, "SAFE_ENTRY_Y": 20, "SAFE_PLACE_X": 25, "SAFE_PLACE_Y": 10}}
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
        cfg = {"auto_sell": True, "auto_sell_timer_enabled": True, "sell_cooldown": 0, "jump_key": "C", "map_profile": {"SAFE_ENTRY_X": 20, "SAFE_ENTRY_Y": 20, "SAFE_PLACE_X": 25, "SAFE_PLACE_Y": 10}}
        app._spotify_custom_safe_entry_step = types.MethodType(lambda self, cfg, pos, now: "PENDING", app)
        result = pro.MapleNghiaPro._spotify_mainfarm_sell_safe_stage(app, cfg, (15, 20), 100.0, owner="V10_STRATEGY")
        self.assertEqual(result, "STOP_TICK")
        self.assertEqual(app.behavior_engine.safe_calls, 0)
        self.assertEqual(app.run_sell_calls, 0)
        app._spotify_custom_safe_entry_step = types.MethodType(lambda self, cfg, pos, now: "READY", app)
        result = pro.MapleNghiaPro._spotify_mainfarm_sell_safe_stage(app, cfg, (25, 10), 100.1, owner="V10_STRATEGY")
        self.assertEqual(result, "STOP_TICK")
        self.assertEqual(app.behavior_engine.safe_calls, 1)
        self.assertEqual(app.run_sell_calls, 1)

    def test_builder_ui_has_safe_entry_and_still_no_farm_return_slot(self):
        text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
        self.assertIn('"SAFE_ENTRY": "SAFE ENTRY"', text)
        self.assertIn('("LEFT", "RIGHT", "SAFE_ENTRY", "SAFE")', text)
        self.assertNotIn('"FARM_RETURN":', text)
        self.assertNotIn('"FARM RETURN"', text)

    def test_safe_failure_resets_safe_entry_for_next_sell_attempt(self):
        app = self.make_app()
        app.spotify_sell_timer_event.set()
        app.behavior_engine.safe_result = "FAILED"
        app.spotify_custom_safe_entry_state = "DONE"
        cfg = {"auto_sell": True, "auto_sell_timer_enabled": True, "sell_cooldown": 0, "jump_key": "C", "map_profile": {"SAFE_ENTRY_X": 20, "SAFE_ENTRY_Y": 20, "SAFE_PLACE_X": 25, "SAFE_PLACE_Y": 10}}
        result = pro.MapleNghiaPro._spotify_mainfarm_sell_safe_stage(app, cfg, (25, 10), 100.0, owner="V10_STRATEGY")
        self.assertEqual(result, "STOP_TICK")
        self.assertEqual(app.spotify_custom_safe_entry_state, "MOVE_ENTRY")

    def test_no_safe_entry_keeps_existing_direct_safe_behavior(self):
        app = self.make_app()
        app.spotify_sell_timer_event.set()
        cfg = {"auto_sell": True, "auto_sell_timer_enabled": True, "sell_cooldown": 0, "jump_key": "C", "map_profile": {"SAFE_PLACE_X": 25, "SAFE_PLACE_Y": 10}}
        result = pro.MapleNghiaPro._spotify_mainfarm_sell_safe_stage(app, cfg, (25, 10), 100.0, owner="V10_STRATEGY")
        self.assertEqual(result, "STOP_TICK")
        self.assertEqual(app.behavior_engine.safe_calls, 1)
        self.assertEqual(app.run_sell_calls, 1)

    def test_return_to_farm_request_requires_safe_entry(self):
        engine, _ = _strategy(safe_entry=None)
        self.assertFalse(engine.request_post_sell_return_to_farm())
        engine2, _ = _strategy(safe_entry=(20, 20))
        self.assertTrue(engine2.request_post_sell_return_to_farm())
        self.assertTrue(engine2.return_to_farm_pending)

    def test_return_to_farm_moves_to_safe_entry_x_down_jumps_and_confirms_lane_y(self):
        engine, host = _strategy(safe_entry=(20, 20))
        self.assertTrue(engine.request_post_sell_return_to_farm())
        cfg = {"jump_key": "C", "left_key": "LEFT", "right_key": "RIGHT"}
        self.assertTrue(engine._post_sell_return_to_farm_step(cfg, (12, 0), 20.0))
        self.assertEqual(host.moves[-1], "RIGHT")
        self.assertEqual(host.behavior_engine.core.down_jump_calls, 0)
        self.assertTrue(engine._post_sell_return_to_farm_step(cfg, (20, 0), 20.1))
        self.assertEqual(host.behavior_engine.core.down_jump_calls, 1)
        self.assertTrue(engine.return_to_farm_pending)
        self.assertTrue(engine._post_sell_return_to_farm_step(cfg, (20, 5), 20.3))
        self.assertFalse(engine._post_sell_return_to_farm_step(cfg, (20, 20), 20.7))
        self.assertFalse(engine.return_to_farm_pending)

    def test_return_to_farm_waits_until_miumiu_releases_input_ownership(self):
        engine, host = _strategy(safe_entry=(20, 20))
        self.assertTrue(engine.request_post_sell_return_to_farm())
        cfg = {"jump_key": "C", "left_key": "LEFT", "right_key": "RIGHT"}
        host.spotify_sell_inflight = True
        self.assertTrue(engine._post_sell_return_to_farm_step(cfg, (20, 0), 30.0))
        self.assertEqual(host.behavior_engine.core.down_jump_calls, 0)
        host.spotify_sell_inflight = False
        host.sell_lock.acquire()
        try:
            self.assertTrue(engine._post_sell_return_to_farm_step(cfg, (20, 0), 30.1))
            self.assertEqual(host.behavior_engine.core.down_jump_calls, 0)
        finally:
            host.sell_lock.release()

    def test_tick_blocks_combat_until_post_sell_return_reaches_farm_lane(self):
        engine, host = _strategy(safe_entry=(20, 20))
        self.assertTrue(engine.request_post_sell_return_to_farm())
        cfg = {
            "jump_key": "C", "left_key": "LEFT", "right_key": "RIGHT",
            "spotify_attack_key": "X", "tele_enabled": False, "auto_loot": False,
            "pause_on_focus_loss": False,
        }
        self.assertTrue(engine.tick(cfg, (12, 0), 40.0))
        self.assertEqual(host.behavior_engine.core.combat_calls, 0)
        self.assertTrue(engine.return_to_farm_pending)

    def test_successful_seller_wires_return_to_farm_but_not_farm_return_feature(self):
        pro_text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
        strategy_text = (APP / "nghia_strategy_v10.py").read_text(encoding="utf-8")
        self.assertIn("request_post_sell_return_to_farm", pro_text)
        self.assertIn("_post_sell_return_to_farm_step", strategy_text)
        self.assertIn("_spotify_jump_down_reconstructed(cfg)", strategy_text)
        self.assertNotIn("FARM_RETURN", pro_text)
        self.assertNotIn("FARM_RETURN", strategy_text)


if __name__ == "__main__":
    unittest.main()
