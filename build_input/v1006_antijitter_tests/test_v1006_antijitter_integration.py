from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'portable' / 'app_payload'


def test_core_wires_antijitter_into_all_movement_profiles_without_owning_input():
    src = (APP / 'spotify_recovered_core.py').read_text(encoding='utf-8')
    assert 'from nghia_anti_jitter import AntiJitterManager' in src
    assert '"SIMPLE"' in src and 'edge_should_turn' in src
    assert '"PIRATE2:FARM"' in src
    assert '"PIRATE2_1HIT:MOVE"' in src
    assert '"BUNNY:TO_B"' in src
    assert '"BUNNY:TO_A"' in src
    assert '"STAND:ANCHOR_DRIFT"' in src
    # Gate is advisory only; it must never send input itself.
    anti = (APP / 'nghia_anti_jitter.py').read_text(encoding='utf-8')
    for forbidden in ('keyDown(', 'keyUp(', 'press(', 'set_move(', 'release_move('):
        assert forbidden not in anti


def test_ui_has_live_toggle_and_off_is_documented_as_v1006_original():
    src = (APP / 'maple_nghia_pro.py').read_text(encoding='utf-8')
    assert 'self.anti_jitter_enabled = tk.BooleanVar(value=False)' in src
    assert 'Anti-Jitter / Hysteresis' in src
    assert 'OFF = V10.0.6 gốc' in src
    assert '"anti_jitter_enabled": bool(self.anti_jitter_enabled.get())' in src
    assert '"anti_jitter_enabled": self.anti_jitter_enabled.get()' in src
    assert '"anti_jitter_enabled"' in src.split('bool_vars = [', 1)[1]
    assert 'command=self._on_anti_jitter_toggle' in src


def test_live_toggle_updates_runtime_cfg_and_resets_gate_when_disabled():
    src = (APP / 'maple_nghia_pro.py').read_text(encoding='utf-8')
    assert 'def _on_anti_jitter_toggle(self):' in src
    assert 'self.runtime_cfg["anti_jitter_enabled"] = enabled' in src
    assert 'self.nghia_anti_jitter_manager.reset()' in src


def test_stop_nonblocking_hotfix_is_still_present():
    src = (APP / 'maple_nghia_pro.py').read_text(encoding='utf-8')
    # Guard against accidentally basing the candidate on old V10.0.3 source.
    assert 'self._stop_requested = threading.Event()' in src
    assert 'self._stop_cleanup_thread = None' in src
    assert 'Đã nhận STOP; đã khóa worker mới, đang nhả input nền.' in src
