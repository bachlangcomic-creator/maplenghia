from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'app_payload' / 'nghia_spotify_nologin.py'


def test_actual_run_bat_ui_exposes_antijitter_toggle_in_map_block():
    src = ENTRY.read_text(encoding='utf-8')
    block = src.split('    def _map_block(self):', 1)[1].split('    def _game_window_block(self):', 1)[0]
    assert 'Anti-Jitter / Hysteresis' in block
    assert 'variable=self.anti_jitter_enabled' in block
    assert 'command=self._on_anti_jitter_toggle' in block
