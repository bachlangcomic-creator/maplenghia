import ast
import os
from pathlib import Path

APP = Path(os.environ.get("APP_PAYLOAD", Path(__file__).resolve().parents[3]))
OVERLAY = Path(__file__).resolve().parents[1]


def _fn(name):
    text=(APP/'maple_nghia_pro.py').read_text(encoding='utf-8'); tree=ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef) and node.name==name:
            return ast.get_source_segment(text,node) or ''
    raise AssertionError(name)


def _production_text():
    parts=[(APP/'maple_nghia_pro.py').read_text(encoding='utf-8')]
    for name in ('spotify_detection_parity.py','spotify_watchdog.py','spotify_all_cure_market.py','spotify_exact_assets.py'):
        parts.append((OVERLAY/name).read_text(encoding='utf-8'))
    return '\n'.join(parts)


def test_v98_has_no_session_enforcement_runtime_path():
    text=_production_text()
    for forbidden in ('SpotifySessionMonitorWorker','session_monitor_worker','check_session(','session_token','KICK:'):
        assert forbidden not in text


def test_v98_captcha_runtime_has_no_solver_or_generative_ai():
    text=_production_text().lower()
    for forbidden in ('google.generativeai','generativeai','solve_captcha','captcha_answer','gemini'):
        assert forbidden not in text


def test_stop_invalidates_market_watchdog_before_combat_shutdown():
    src=_fn('stop_bot')
    assert src.index('spotify_all_cure_market.stop()') < src.index('spotify_watchdog.stop()') < src.index('behavior_engine.stop()')


def test_revive_and_market_release_farm_ownership_before_side_effects():
    revive=_fn('_spotify_watchdog_request_revive')
    market=_fn('_spotify_market_run_action')
    assert revive.index('_spotify_watchdog_request_pause') < revive.index('pydirectinput.moveTo')
    assert market.index('behavior_engine.release_inputs()') < market.index('return False')


def test_c2_worker_contains_no_watchdog_market_or_miumiu_side_effect_calls():
    src=_fn('_c2_fast_farm_worker').lower()
    for forbidden in ('watchdog','all_cure','market','miumiu','run_sell_thread','captcha','full_bag'):
        assert forbidden not in src
