import spotify_detection_parity as d


def test_disconnect_threshold_is_recovered_095():
    assert d.DISCONNECT_THRESHOLD == 0.95


def test_disconnect_recovered_uses_exact_asset_but_structural_path_label(monkeypatch):
    seen = {}
    monkeypatch.setattr(d, "verify_exact_asset", lambda name: name == "ONL_B64")
    monkeypatch.setattr(d, "decode_exact_asset", lambda name: b"PNG")

    def matcher(frame, raw):
        seen["raw"] = raw
        return 0.951

    result = d.detect_disconnect_recovered(object(), matcher)
    assert seen["raw"] == b"PNG"
    assert result.kind == "disconnect"
    assert result.matched
    assert result.threshold == 0.95
    assert result.source == d.SOURCE_STRUCTURAL
