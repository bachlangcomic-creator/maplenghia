from __future__ import annotations
import ast, hashlib, json, sys
from pathlib import Path
APP = Path(sys.argv[1] if len(sys.argv) > 1 else 'portable/app_payload').resolve()
ROOT = APP.parent
UNCHANGED = {
    'nghia_watchdog_client_capture.py': '80dfabe995f535339d404a332ea5ebde608bb1189984a6d9498206dc9c7c677c',
    'spotify_watchdog.py': '4feaa4debf6e99f960e0058b3e43111b557317b2fa347ecf4531752079e75c79',
    'spotify_pc_alarm.py': 'a6c83df75b748e6a6ee398273aa8350ec5138c0f6cb64e77d6c31b1bf42ee3f4',
    'spotify_detection_parity.py': '479a6a5e9d2482fe26d040c5014e0bff61fda75426e8e690c0a173ebb002c2a1',
    'spotify_recovered_core.py': '7bd043a7615d97c533acc157c4a0112e5f3ffe32388c88e462c0fb36e6452048',
    'nghia_adaptive_y_ui.py': '7bc0744ffebdb645ebd6e72466aec3890b23fb5e22486be3a78ba5b6794c87ce',
    'nghia_anti_jitter.py': '25ac99c6f5c84d736d641c3c40ac33c3127f4bfd80f6bf46fec09baac899cf0e',
    'maps.json': '52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d',
    'spotify_behavior_engine.py': '8f85f95917e898007a83ebb13337cae702c6b1ec401f7af571fb46dd8604d01e',
    'spotify_main_farm_orchestrator.py': '1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68',
}
CHANGED = {
    'maple_nghia_pro.py': '5c31d001ba68ac71d1e28e9123b5d6a40c841a1c2704c9a173b621bb4ea822cc',
    'nghia_strategy_v10.py': '59d899d88cce70424dcef7d8954248926807046c8bb85ee638430a532bb23dfb',
    'nghia_spotify_nologin.py': '8b064be4d4318176274350647926c3d592d023d99d707f81c43591d2e5a6ccbf',
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

for rel, expected in {**UNCHANGED, **CHANGED}.items():
    got = sha(APP / rel)
    if got != expected:
        raise SystemExit(f'hash mismatch {rel}: {got} != {expected}')

strategy = (APP/'nghia_strategy_v10.py').read_text(encoding='utf-8')
for token in (
    'safe_entry: Optional[Tuple[float, float]] = None',
    'farm_return: Optional[Tuple[float, float]] = None',
    'SAFE_ENTRY_X', 'FARM_RETURN_X',
    'def _custom_sell_entry_step', 'def request_post_sell_return',
    'def _custom_farm_return_step', '_spotify_jump_down_reconstructed',
    'rest_ms = random.randint(1000, 1500)',
):
    if token not in strategy:
        raise SystemExit(f'missing V10.0.16 strategy token: {token}')

controller=(APP/'maple_nghia_pro.py').read_text(encoding='utf-8')
for token in (
    '"SAFE_ENTRY": "SAFE ENTRY"', '"FARM_RETURN": "FARM RETURN"',
    '("LEFT", "RIGHT", "SAFE_ENTRY", "SAFE", "FARM_RETURN")',
    'safe_entry=captured["SAFE_ENTRY"]', 'farm_return=captured["FARM_RETURN"]',
    'entry_outcome = self.strategy_v10._custom_sell_entry_step',
    'request_post_sell_return',
    'timer_mode = bool(cfg.get("auto_sell_timer_enabled"))',
    'trigger_due = timer_due if timer_mode else full_bag_due',
):
    if token not in controller:
        raise SystemExit(f'missing controller token: {token}')

tree=ast.parse(controller); lines=controller.splitlines()
expected_funcs={
    'build_simple_map_profile':'070327a767f8aa97ba53bb8324a6db09eef7ea05032985881fcd53214b36ad3b',
    'build_pirate_map_profile':'70fdc0e7cfbcce199b99be04ccce9324255769e933c5254f309e6cd0434912a3',
    '_spotify_profile_kind_from':'d2e3f04a3852a3244270b8a1d966b797e95b6887523d276ac8c0421a3880a32b',
}
for name, expected in expected_funcs.items():
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
    src='\n'.join(lines[node.lineno-1:node.end_lineno])+'\n'
    got=hashlib.sha256(src.encode()).hexdigest()
    if got != expected:
        raise SystemExit(f'original-map function changed {name}: {got}')

ui=(APP/'nghia_spotify_nologin.py').read_text(encoding='utf-8')
if 'V10.0.16' not in ui or '10.0.15' in ui:
    raise SystemExit('compact UI version markers not fully promoted to V10.0.16')
if 'random.uniform(3.0, 5.0)' in strategy:
    raise SystemExit('V10.0.15 Human Rest regression')

vf=ROOT/'version.json'
if vf.exists():
    version=json.loads(vf.read_text(encoding='utf-8'))
    if version.get('version') != '10.0.16':
        raise SystemExit(f'version.json mismatch: {version}')
print('V1016_VERIFY_OK', {rel:sha(APP/rel) for rel in CHANGED})
