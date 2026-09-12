from pathlib import Path
import ast,json,os
import spotify_detection_parity as d
APP=Path(os.environ['APP_PAYLOAD'])
def source_fn(path,name):
    text=Path(path).read_text(encoding='utf-8');tree=ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef) and node.name==name:return ast.get_source_segment(text,node) or ''
    raise AssertionError(name)
def test_v981_hold_combo_and_onehit_protections():
    core=APP/'spotify_recovered_core.py';primary=source_fn(core,'_spotify_primary_skill_step');onehit=source_fn(core,'_spotify_pirate_1hit_farm_step');assert '_spotify_hold_combo_action' in primary;assert '_spotify_c2_tp_skill_hold_combo' not in primary;assert '_spotify_hold_combo_action' not in onehit
def test_disconnect_threshold_is_direct_constant_with_structural_path():
    assert d.DISCONNECT_THRESHOLD==0.95;src=source_fn(APP/'spotify_detection_parity.py','detect_disconnect_recovered');assert 'DISCONNECT_THRESHOLD' in src and 'SOURCE_STRUCTURAL' in src
def test_forbidden_runtime_paths_absent_from_v99_production_units():
    names=('maple_nghia_pro.py','spotify_recovered_core.py','spotify_detection_parity.py','spotify_watchdog.py','spotify_all_cure_executor.py','spotify_all_cure_market.py','spotify_main_farm_orchestrator.py');text='\n'.join((APP/n).read_text(encoding='utf-8') for n in names).lower()
    for forbidden in ('session_monitor_worker','check_session(','session_token','gemini','generativeai','solve_captcha','captcha_answer'):assert forbidden not in text,forbidden
def test_c2_hot_worker_excludes_watchdog_market_and_sell():
    src=source_fn(APP/'maple_nghia_pro.py','_c2_fast_farm_worker').lower()
    for forbidden in ('watchdog','all_cure','market','miumiu','run_sell_thread'):assert forbidden not in src,forbidden
def test_all_cure_external_path_and_evidence_labels_are_locked():
    market=(APP/'spotify_all_cure_market.py').read_text(encoding='utf-8');assert "'user_data' / 'all_cure_images'" in market;allowed={'direct','high_structural','nghia_fallback'};ev_root=Path(os.environ['V990_EVIDENCE'])
    def walk(v):
        if isinstance(v,dict):
            if 'evidence' in v:assert v['evidence'] in allowed
            for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    for p in ev_root.glob('*.json'):walk(json.loads(p.read_text(encoding='utf-8')))
def test_all_cure_workflow_is_fail_closed_until_evidence_complete():
    data=json.loads((Path(os.environ['V990_EVIDENCE'])/'all_cure_market.json').read_text(encoding='utf-8'));assert data['workflow_evidence_ready'] is False
