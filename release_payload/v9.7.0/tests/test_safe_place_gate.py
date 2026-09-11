import inspect

from spotify_recovered_core import SpotifyRecoveredCore

CFG = {"map_profile": {"SAFE_PLACE_X": 67, "SAFE_PLACE_Y": 161}}


def test_safe_place_settle_precedes_verify(fake_host, monkeypatch):
    core = SpotifyRecoveredCore(fake_host)
    monkeypatch.setattr(SpotifyRecoveredCore, "_spotify_move_to_step", lambda *a, **k: True)
    assert core._spotify_safe_place_step(CFG, (67, 161), 10.0) == "PENDING"
    assert fake_host.spotify_r54_safe_state == "SETTLE_SAFE"
    assert fake_host.spotify_r54_safe_verify_count == 0


def test_safe_place_success_on_first_valid_verify(fake_host):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_r54_safe_state = "VERIFY_SAFE"
    fake_host.spotify_r54_safe_arrived_at = 8.0
    fake_host.spotify_r54_safe_verify_count = 0
    assert core._spotify_safe_place_step(CFG, (67, 161), 10.0) == "READY"
    assert fake_host.spotify_r54_safe_state == "SAFE_OK"


def test_safe_place_fails_closed_after_six_bad_observations(fake_host):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_r54_safe_state = "VERIFY_SAFE"
    fake_host.spotify_r54_safe_arrived_at = 8.0
    for expected in range(1, 6):
        assert core._spotify_safe_place_step(CFG, (10, 10), 10.0 + expected) == "PENDING"
        assert fake_host.spotify_r54_safe_verify_count == expected
    assert core._spotify_safe_place_step(CFG, (10, 10), 16.0) == "FAILED"
    assert fake_host.spotify_r54_safe_verify_count == 6
    assert fake_host.spotify_r54_safe_state == "SAFE_FAIL"


def test_safe_reset_helper_restores_move_state(fake_host):
    core = SpotifyRecoveredCore(fake_host)
    fake_host.spotify_r54_safe_state = "SAFE_FAIL"
    fake_host.spotify_r54_safe_arrived_at = 5.0
    fake_host.spotify_r54_safe_verify_count = 6
    core._spotify_reset_safe_place_state()
    assert fake_host.spotify_r54_safe_state == "MOVE_SAFE"
    assert fake_host.spotify_r54_safe_arrived_at == 0.0
    assert fake_host.spotify_r54_safe_verify_count == 0


def test_missing_safe_coordinates_fail_closed(fake_host):
    core = SpotifyRecoveredCore(fake_host)
    assert core._spotify_safe_place_step({"map_profile": {}}, (67, 161), 10.0) == "FAILED"
    assert fake_host.spotify_r54_safe_state == "SAFE_FAIL"


def test_safe_verify_uses_existing_tolerance_and_no_new_retry_sleep():
    src = inspect.getsource(SpotifyRecoveredCore._spotify_safe_place_step)
    assert "SPOTIFY_SAFE_MAX_VERIFY_ATTEMPTS" in src
    assert "time.sleep(" not in src
