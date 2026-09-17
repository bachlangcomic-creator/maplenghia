from __future__ import annotations

import ctypes
import os
import sys
import threading
import types
import unittest
from pathlib import Path

import cv2
import numpy as np

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload")).resolve()
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

if not hasattr(ctypes, "windll"):
    class _DummyUser32:
        def __getattr__(self, name):
            return lambda *args, **kwargs: 0
    ctypes.windll = types.SimpleNamespace(user32=_DummyUser32())

import spotify_detection_parity as parity
from spotify_detection_parity import SpotifyDetectionResult
from spotify_exact_assets import decode_exact_asset
from spotify_watchdog import SpotifyWatchdogWorker
import maple_nghia_pro as pro


class CaptchaV1019Tests(unittest.TestCase):
    def test_detection_parity_exposes_multiscale_and_three_frame_hysteresis(self):
        self.assertEqual(tuple(parity.CAPTCHA_SCALES), (0.90, 0.95, 1.00, 1.05, 1.10))
        self.assertEqual(parity.CAPTCHA_CLEAR_FRAMES, 3)
        self.assertTrue(hasattr(parity, "CaptchaAlertState"))

    def test_multiscale_lie_detects_090_scaled_template(self):
        raw = decode_exact_asset("LIE_B64")
        tpl = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        scaled = cv2.resize(
            tpl,
            (
                max(1, int(round(tpl.shape[1] * 0.90))),
                max(1, int(round(tpl.shape[0] * 0.90))),
            ),
            interpolation=cv2.INTER_AREA,
        )
        roi = np.zeros((350, 650, 3), dtype=np.uint8)
        patch = cv2.cvtColor(scaled, cv2.COLOR_GRAY2RGB)
        roi[100 : 100 + patch.shape[0], 120 : 120 + patch.shape[1]] = patch
        host = object.__new__(pro.MapleNghiaPro)
        score, center, scale = pro.MapleNghiaPro._spotify_watchdog_exact_template_match_multiscale(
            host, roi, "LIE_B64"
        )
        self.assertGreaterEqual(score, 0.70)
        self.assertAlmostEqual(scale, 0.90, places=2)
        self.assertIsNotNone(center)

    def test_captcha_state_alerts_once_and_clears_after_three_clean_frames(self):
        state = parity.CaptchaAlertState(clear_frames=3)
        T = parity.CaptchaTransition
        self.assertEqual(state.update(True), T.APPEARED)
        self.assertEqual(state.update(True), T.PRESENT)
        self.assertEqual(state.update(False), T.PRESENT)
        self.assertEqual(state.update(False), T.PRESENT)
        self.assertEqual(state.update(False), T.CLEARED)
        self.assertEqual(state.update(False), T.ABSENT)

    def test_watchdog_emits_unmatched_captcha_result_so_clear_can_be_observed(self):
        got = []
        emitted = threading.Event()

        class Host:
            runtime_cfg = {"spotify_watchdog_parity_enabled": True}

            def _spotify_watchdog_interval(self, cfg):
                return 0.001

            def _spotify_cached_game_hwnd(self):
                return 1

            def _spotify_watchdog_capture_frame(self, cfg, hwnd):
                return object()

            def _spotify_watchdog_scan_frame(self, frame, cfg):
                return [
                    SpotifyDetectionResult(
                        "captcha", False, 0.1, 0.7, "spotify_exact"
                    )
                ]

            def _spotify_watchdog_emit(self, result, cfg):
                got.append(result)
                emitted.set()

            def _spotify_watchdog_sell_timer_due(self, cfg):
                pass

            def _log(self, text):
                pass

        worker = SpotifyWatchdogWorker(Host())
        worker.start({"spotify_watchdog_parity_enabled": True})
        try:
            self.assertTrue(
                emitted.wait(0.25),
                "unmatched captcha result was filtered before emit",
            )
        finally:
            worker.stop()
        self.assertEqual(len(got), 1)
        self.assertFalse(got[0].matched)


if __name__ == "__main__":
    unittest.main()
