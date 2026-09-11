import importlib

import numpy as np
import pytest


def detector_module():
    try:
        return importlib.import_module("spotify_detection_parity")
    except ModuleNotFoundError:
        pytest.fail("spotify_detection_parity module is missing")


def test_recovered_detector_constants_are_not_conflated():
    d = detector_module()
    assert d.CAPTCHA_ROI == (300, 200, 650, 350)
    assert d.CAPTCHA_PRIMARY_THRESHOLD == 0.70
    assert d.CAPTCHA_SECONDARY_THRESHOLD == pytest.approx(0.68)
    assert d.FULL_BAG_DETECT_THRESHOLD == 0.35
    assert d.SELL_THRESHOLD == 0.65
    assert d.SOURCE_EXACT == "spotify_exact"
    assert d.SOURCE_STRUCTURAL == "spotify_structural"
    assert d.SOURCE_NGHIA_FALLBACK == "nghia_fallback"


def test_exact_captcha_roi_only_accepts_1280x720():
    d = detector_module()
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    roi = d.crop_captcha_roi(frame, (1280, 720))
    assert roi.shape[:2] == (350, 650)
    with pytest.raises(ValueError):
        d.crop_captcha_roi(np.zeros((900, 1600, 3), dtype=np.uint8), (1600, 900))


def test_fallback_can_never_claim_spotify_exact():
    d = detector_module()
    r = d.score_result("captcha", 0.99, 0.86, d.SOURCE_NGHIA_FALLBACK)
    assert r.matched and r.source == d.SOURCE_NGHIA_FALLBACK
    with pytest.raises(ValueError):
        d.score_result("captcha", 0.99, 0.70, d.SOURCE_EXACT)


def test_structural_threshold_is_allowed_but_not_exact():
    d = detector_module()
    r = d.score_result("full_bag", 0.40, d.FULL_BAG_DETECT_THRESHOLD, d.SOURCE_STRUCTURAL)
    assert r.matched
    assert r.source == d.SOURCE_STRUCTURAL
    assert r.source != d.SOURCE_EXACT
