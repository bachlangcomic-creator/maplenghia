import pytest


class FakeFrame:
    def __getitem__(self, key):
        rows, cols = key
        height = int(rows.stop) - int(rows.start)
        width = int(cols.stop) - int(cols.start)
        return type("FakeRoi", (), {"shape": (height, width, 3)})()


def test_exact_label_requires_verified_asset_and_exact_path():
    import spotify_detection_parity as d

    exact = d.exact_asset_result("captcha", 0.71, 0.70, "LIE_B64", path_is_exact=True)
    assert exact.matched and exact.source == d.SOURCE_EXACT
    structural = d.exact_asset_result("dead", 0.99, 0.86, "DEAD_B64", path_is_exact=False)
    assert structural.matched and structural.source == d.SOURCE_STRUCTURAL


def test_captcha_exact_is_1280x720_only():
    import spotify_detection_parity as d

    with pytest.raises(ValueError):
        d.detect_captcha_exact(FakeFrame(), (1600, 900), lambda roi, raw: 0.99)


def test_captcha_exact_uses_recovered_roi_asset_and_threshold():
    import spotify_detection_parity as d

    seen = {}
    def matcher(roi, raw):
        seen["shape"] = roi.shape
        seen["png"] = raw[:8]
        return 0.71

    result = d.detect_captcha_exact(FakeFrame(), (1280, 720), matcher)
    assert seen["shape"][:2] == (350, 650)
    assert seen["png"] == b"\x89PNG\r\n\x1a\n"
    assert result.matched
    assert result.threshold == 0.70
    assert result.source == d.SOURCE_EXACT


def test_full_bag_variant_keeps_035_separate_from_sell_065():
    import spotify_detection_parity as d

    exact = d.score_full_bag_variant("INV_FULL_B64", 0.36, path_is_exact=True)
    structural = d.score_full_bag_variant("INV_FULL_2_B64", 0.36, path_is_exact=False)
    assert exact.matched and exact.threshold == 0.35 and exact.source == d.SOURCE_EXACT
    assert structural.matched and structural.source == d.SOURCE_STRUCTURAL
    assert d.SELL_THRESHOLD == 0.65


def test_dead_and_disconnect_require_explicit_threshold_when_path_not_recovered():
    import spotify_detection_parity as d

    dead = d.score_dead(0.91, threshold=0.86, path_is_exact=False)
    dc = d.score_disconnect(0.91, threshold=0.86, path_is_exact=False)
    assert dead.source == d.SOURCE_STRUCTURAL
    assert dc.source == d.SOURCE_STRUCTURAL
    assert dead.threshold == dc.threshold == 0.86


def test_captcha_module_has_no_solver_or_gemini_path():
    import inspect
    import spotify_detection_parity as d

    text = inspect.getsource(d).lower()
    for forbidden in ("gemini", "generativeai", "google.generative", "solve_captcha", "captcha_answer"):
        assert forbidden not in text
