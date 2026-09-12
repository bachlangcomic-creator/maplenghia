import ast
import json
import os
from pathlib import Path

APP = Path(os.environ.get("APP_PAYLOAD", Path(__file__).resolve().parents[3]))
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence" / "main_farm_worker.json"


def _fn(name):
    text=(APP/'maple_nghia_pro.py').read_text(encoding='utf-8'); tree=ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name==name:
            return ast.get_source_segment(text,node) or ''
    raise AssertionError(name)


def test_main_farm_evidence_maps_to_existing_serialized_owner_without_thread_guess():
    data=json.loads(EVIDENCE.read_text(encoding='utf-8'))
    assert data['ownership'] == [
        'periodic_loot_buff_pet', 'auto_sell_safe_place', 'farm_mode_dispatch', 'lost_player_recovery'
    ]
    assert data['start_order'] == []
    bot=_fn('bot_loop')
    assert '_run_periodic_actions' in bot
    assert 'safe_place_step' in bot and 'run_sell_thread' in bot
    assert 'behavior_engine.tick' in bot
    assert '_c2_fast_worker_owns' in bot


def test_main_farm_worker_recovery_does_not_create_speculative_new_thread():
    text=(APP/'maple_nghia_pro.py').read_text(encoding='utf-8')
    assert 'Nghia-Spotify-MainFarm' not in text
    c2=_fn('_c2_fast_farm_worker')
    assert 'behavior_engine.tick' in c2
