import sys
from pathlib import Path

APP = (Path(__file__).resolve().parents[1] / 'portable' / 'app_payload').resolve()
sys.path.insert(0, str(APP))

from nghia_anti_jitter import AntiJitterManager


def test_off_is_true_bypass_and_clears_stale_state():
    gate = AntiJitterManager()
    # Build stale ON state first.
    gate.observe_lane('simple', True, 99, 0, 100, 5, 0.0)
    assert gate.edge_should_turn('simple', True, 'RIGHT', 99, 0, 100, 5, 0.0) is False
    assert gate.edge_should_turn('simple', True, 'RIGHT', 99, 0, 100, 5, 0.05) is True
    # OFF must bypass immediately and clear any lock/debounce state.
    assert gate.edge_should_turn('simple', False, 'RIGHT', 99, 0, 100, 5, 0.06) is True
    snap = gate.snapshot('simple')
    assert snap['last_edge'] == ''
    assert snap['candidate_count'] == 0
    assert snap['lock_until'] == 0.0


def test_on_requires_two_consecutive_edge_samples():
    gate = AntiJitterManager(confirm_frames=2)
    gate.observe_lane('simple', True, 96, 0, 100, 5, 1.00)
    assert gate.edge_should_turn('simple', True, 'RIGHT', 96, 0, 100, 5, 1.00) is False
    gate.observe_lane('simple', True, 97, 0, 100, 5, 1.05)
    assert gate.edge_should_turn('simple', True, 'RIGHT', 97, 0, 100, 5, 1.05) is True


def test_same_edge_cannot_retrigger_until_departure_and_lock_expire():
    gate = AntiJitterManager(confirm_frames=2, lock_seconds=0.40, departure_pixels=8.0)
    gate.observe_lane('simple', True, 96, 0, 100, 5, 2.00)
    gate.edge_should_turn('simple', True, 'RIGHT', 96, 0, 100, 5, 2.00)
    gate.observe_lane('simple', True, 97, 0, 100, 5, 2.05)
    assert gate.edge_should_turn('simple', True, 'RIGHT', 97, 0, 100, 5, 2.05) is True

    # Still around the same edge: block even after the timer if it never departed.
    gate.observe_lane('simple', True, 94, 0, 100, 5, 2.60)
    assert gate.edge_should_turn('simple', True, 'RIGHT', 94, 0, 100, 5, 2.60) is False

    # Departure threshold is right_x - tolerance - 8 = 87.
    gate.observe_lane('simple', True, 86, 0, 100, 5, 2.65)
    assert gate.snapshot('simple')['departed'] is True

    # Returning later still needs two fresh edge frames.
    gate.observe_lane('simple', True, 96, 0, 100, 5, 3.00)
    assert gate.edge_should_turn('simple', True, 'RIGHT', 96, 0, 100, 5, 3.00) is False
    gate.observe_lane('simple', True, 97, 0, 100, 5, 3.05)
    assert gate.edge_should_turn('simple', True, 'RIGHT', 97, 0, 100, 5, 3.05) is True


def test_middle_frame_breaks_consecutive_confirmation():
    gate = AntiJitterManager(confirm_frames=2)
    gate.observe_lane('simple', True, 96, 0, 100, 5, 4.00)
    assert gate.edge_should_turn('simple', True, 'RIGHT', 96, 0, 100, 5, 4.00) is False
    # A middle-lane frame resets the edge candidate.
    gate.observe_lane('simple', True, 50, 0, 100, 5, 4.05)
    gate.observe_lane('simple', True, 96, 0, 100, 5, 4.10)
    assert gate.edge_should_turn('simple', True, 'RIGHT', 96, 0, 100, 5, 4.10) is False


def test_confirm_gate_debounces_waypoints_and_off_bypasses():
    gate = AntiJitterManager(confirm_frames=2)
    assert gate.confirm('bunny:B', True, True, 5.00) is False
    assert gate.confirm('bunny:B', True, True, 5.05) is True
    assert gate.confirm('bunny:B', False, True, 5.10) is False
    assert gate.confirm('bunny:B', True, False, 5.15) is True


def test_fail_open_on_bad_lane_values():
    gate = AntiJitterManager()
    # Bad values must never become a reason to freeze movement.
    assert gate.edge_should_turn('simple', True, 'RIGHT', 'bad', 0, 100, 5, 6.0) is True


def test_confirm_gate_stays_latched_while_condition_remains_true():
    gate = AntiJitterManager(confirm_frames=2)
    assert gate.confirm('stand:drift', True, True, 7.00) is False
    assert gate.confirm('stand:drift', True, True, 7.05) is True
    # Once confirmed, sustained drift stays confirmed until the condition clears.
    assert gate.confirm('stand:drift', True, True, 7.10) is True
    assert gate.confirm('stand:drift', False, True, 7.15) is False
    assert gate.confirm('stand:drift', True, True, 7.20) is False
