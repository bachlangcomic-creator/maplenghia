import ast
import json
import os
import tempfile
from pathlib import Path

root = Path('portable/app_payload')
main = root / 'maple_nghia_pro.py'
ui = root / 'nghia_spotify_nologin.py'
mt = main.read_text(encoding='utf-8')
ut = ui.read_text(encoding='utf-8')

assert 'LẤY TỌA ĐỘ / THÊM MAP' in mt
assert 'show_coordinate_map_builder' in mt
assert 'map_menu' in mt
assert 'LẤY TỌA ĐỘ / THÊM MAP' in ut
assert 'command=self.show_coordinate_map_builder' in ut
assert 'Nghia Edition V9.9.7' in ut
assert 'NGHIA_LOCAL_VERSION", "9.9.7"' in ut
assert 'Nghia Edition V9.9.6' not in ut

tree = ast.parse(mt)
funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
for name in ('build_simple_map_profile', 'save_map_profile'):
    assert name in funcs

ns = {'Path': Path, 'json': json, 'os': os}
for name in ('build_simple_map_profile', 'save_map_profile'):
    mod = ast.Module(body=[funcs[name]], type_ignores=[])
    ast.fix_missing_locations(mod)
    exec(compile(mod, str(main), 'exec'), ns)

p = ns['build_simple_map_profile']((48.4, 171.2), (183.49, 170.8), (105.2, 162.0))
assert p == {
    'FARM_TYPE': 'SIMPLE',
    'LEFT_X': 48,
    'LEFT_Y': 171,
    'RIGHT_X': 183,
    'RIGHT_Y': 171,
    'SAFE_PLACE_X': 105,
    'SAFE_PLACE_Y': 162,
    'CHAR_MATCH_THRESHOLD': 0.6,
}

with tempfile.TemporaryDirectory() as td:
    target = Path(td) / 'maps.json'
    merged = ns['save_map_profile'](target, {'C1': {'FARM_TYPE': 'SIMPLE'}}, 'NEW', p)
    assert merged['NEW'] == p
    assert json.loads(target.read_text(encoding='utf-8')) == merged

print('V997_COORDINATE_MAP_TESTS_OK')
