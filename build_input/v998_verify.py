from pathlib import Path
import ast

src=Path('portable/app_payload/maple_nghia_pro.py')
text=src.read_text(encoding='utf-8')
assert 'def build_pirate_map_profile(' in text
for token in ('PIRATE ROUTE','LOOT LEFT','LOOT RIGHT','LOOT BOT 1','LOOT BOT 2'):
    assert token in text, token

tree=ast.parse(text)
funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
ns={}
mod=ast.Module(body=[funcs['build_pirate_map_profile']],type_ignores=[])
ast.fix_missing_locations(mod)
exec(compile(mod,str(src),'exec'),ns)
p=ns['build_pirate_map_profile'](
    (84.4,189.2),(180.2,188.4),(155.1,172.2),
    (80.4,196.2),(189.2,196.4),(105.2,201.1),(170.2,201.3),0.6)
expected={
    'FARM_TYPE':'PIRATE_ROUTE','LEFT_X':84,'LEFT_Y':189,
    'RIGHT_X':180,'RIGHT_Y':188,'SAFE_PLACE_X':155,'SAFE_PLACE_Y':172,
    'LOOT_BOT_LEFT_X':80,'LOOT_BOT_LEFT_Y':196,
    'LOOT_BOT_RIGHT_X':189,'LOOT_BOT_RIGHT_Y':196,
    'LOOT_BOT_1_X':105,'LOOT_BOT_1_Y':201,
    'LOOT_BOT_2_X':170,'LOOT_BOT_2_Y':201,'CHAR_MATCH_THRESHOLD':0.6,
}
assert p==expected,(p,expected)
ui=Path('portable/app_payload/nghia_spotify_nologin.py').read_text(encoding='utf-8')
assert 'Nghia Edition V9.9.8' in ui
assert 'NGHIA_LOCAL_VERSION", "9.9.8"' in ui
assert 'LẤY TỌA ĐỘ / THÊM MAP' in ui
print('V998_FEATURE_TESTS_OK')
