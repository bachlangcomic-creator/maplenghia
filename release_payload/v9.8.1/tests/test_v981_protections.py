import ast
import inspect
import os
from pathlib import Path

from spotify_recovered_core import SpotifyRecoveredCore

APP = Path(os.environ.get('APP_PAYLOAD', Path(__file__).resolve().parents[1]))


def function_source(path, name):
    text = Path(path).read_text(encoding='utf-8')
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ''
    raise AssertionError(name)


def test_simple_uses_new_helper_legacy_c2_stays_dormant():
    primary = inspect.getsource(SpotifyRecoveredCore._spotify_primary_skill_step)
    legacy_c2 = inspect.getsource(SpotifyRecoveredCore._spotify_c2_tp_skill_hold_combo)
    core_text = (APP / 'spotify_recovered_core.py').read_text(encoding='utf-8')
    assert '_spotify_hold_combo_action' in primary
    assert '_spotify_c2_tp_skill_hold_combo' not in primary
    assert 'SPOTIFY_R54_COMBO_SPAM_ACTION_MS' in legacy_c2
    assert 'SPOTIFY_R54_COMBO_SPAM_WAIT_S' in legacy_c2
    assert 'SPOTIFY_R54_COMBO_SPAM_ACTION_MS = (20, 50)' in core_text
    assert 'SPOTIFY_R54_COMBO_SPAM_WAIT_S = (0.05, 0.15)' in core_text
    assert 'SPOTIFY_SIMPLE_HOLD_COMBO_MS = (200, 500)' in core_text


def test_one_hit_farm_and_c2_fast_path_stay_protected():
    one_hit = inspect.getsource(SpotifyRecoveredCore._spotify_pirate_1hit_farm_step)
    fast = function_source(APP / 'maple_nghia_pro.py', '_c2_fast_farm_worker')
    assert '_spotify_hold_combo_action' not in one_hit
    assert '_spotify_cached_game_hwnd' in fast
    assert '_find_game_window' not in fast
    for forbidden in ('watchdog','captcha','full_bag','all_cure','market','miumiu','run_sell_thread','dynamic_combo'):
        assert forbidden not in fast.lower(), forbidden


def test_dynamic_combo_remains_single_definition_only():
    core_text = (APP / 'spotify_recovered_core.py').read_text(encoding='utf-8')
    assert core_text.count('_spotify_dynamic_combo_reconstructed(') == 1


def test_forbidden_session_and_captcha_solver_paths_remain_absent():
    production_text = '\n'.join((APP / name).read_text(encoding='utf-8') for name in (
        'maple_nghia_pro.py', 'spotify_recovered_core.py'
    ))
    for forbidden in (
        'SpotifySessionMonitorWorker','session_monitor_worker','check_session(','session_token',
        'google.generativeai','generativeai','solve_captcha','captcha_answer','gemini',
    ):
        assert forbidden.lower() not in production_text.lower(), forbidden
