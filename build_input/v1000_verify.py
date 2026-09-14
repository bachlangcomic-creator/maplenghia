import ast, hashlib, importlib.util, sys
from pathlib import Path

ROOT=Path('portable/app_payload').resolve()

def sha(name):
    return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

PROTECTED={
 'spotify_recovered_core.py':'18e164944d5842629af55ca0f70f274192421515c01ac6451c0bdedf13109d95',
 'spotify_recovered_api.py':'1ceb0d194d1edfcab1a8005ac7fdd04343a90ff6962dc77d2dc675aac06a4339',
 'spotify_behavior_engine.py':'de137e5486518d183e26b83d360fa4a164e0fd136ce1deef003d6ad7b953fe97',
 'spotify_main_farm_orchestrator.py':'1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68',
 'maps.json':'52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d',
}
for name, expected in PROTECTED.items():
    got=sha(name)
    assert got==expected,(name,got,expected)

strategy=ROOT/'nghia_strategy_v10.py'
assert strategy.exists(), 'V10 strategy module missing'
spec=importlib.util.spec_from_file_location('nghia_strategy_v10_verify', strategy)
mod=importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
base={
 'ENGINE_MODE':'STRATEGY_V10','FARM_TYPE':'PIRATE_ROUTE','COMBAT_MODE':'SPOTIFY_COMBO',
 'TP_MODE':'SPAM_TP_SKILL','LOOT_MODE':'PIRATE_BOTTOM_CUSTOM','LEFT_X':80,'LEFT_Y':190,
 'RIGHT_X':190,'RIGHT_Y':190,'SAFE_PLACE_X':155,'SAFE_PLACE_Y':172,
 'LOOT_BOT_LEFT_X':80,'LOOT_BOT_LEFT_Y':196,'LOOT_BOT_RIGHT_X':189,'LOOT_BOT_RIGHT_Y':196,
 'LOOT_BOT_1_X':105,'LOOT_BOT_1_Y':201,'LOOT_BOT_2_X':170,'LOOT_BOT_2_Y':201,
}
assert mod.is_v10_profile(base)
legacy=dict(base); legacy.pop('ENGINE_MODE')
assert not mod.is_v10_profile(legacy)
assert mod.custom_bottom_route_points(base,1)==[(80,196),(105,201),(170,201),(189,196)]
assert mod.custom_bottom_route_points(base,-1)==[(189,196),(170,201),(105,201),(80,196)]
missing=dict(base); missing.pop('LOOT_BOT_2_Y')
try: mod.resolve_v10_profile(missing)
except mod.V10ProfileError as exc: assert 'LOOT_BOT_2_Y' in str(exc)
else: raise AssertionError('missing custom loot field did not fail closed')
invalid=dict(base); invalid['TP_MODE']='MAGIC'
try: mod.resolve_v10_profile(invalid)
except mod.V10ProfileError as exc: assert 'TP_MODE' in str(exc)
else: raise AssertionError('invalid TP mode did not fail closed')

# V10 runtime module must not read/write any legacy Pirate2 state attribute.
tree=ast.parse(strategy.read_text(encoding='utf-8'))
legacy_attrs=sorted({n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute) and n.attr.startswith('spotify_pirate_')})
assert legacy_attrs==[], legacy_attrs

maple=(ROOT/'maple_nghia_pro.py').read_text(encoding='utf-8')
for token in (
 'V10StrategyEngine(self)','V10 PIRATE ROUTE','ENGINE_MODE',
 'legacy_neutral_map_profile()','if not v10_enabled and not self.behavior_engine.handles_profile(cfg):',
 'if not v10_enabled:\n            self.behavior_engine.start(cfg)',
): assert token in maple, token
ui=(ROOT/'nghia_spotify_nologin.py').read_text(encoding='utf-8')
assert 'Nghia Edition V10.0.0' in ui
assert 'NGHIA_LOCAL_VERSION", "10.0.0"' in ui
print('V1000_VERIFY_OK')
