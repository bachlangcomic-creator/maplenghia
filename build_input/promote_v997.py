from pathlib import Path
import json

root = Path('portable')
ui = root / 'app_payload' / 'nghia_spotify_nologin.py'
text = ui.read_text(encoding='utf-8')
count = text.count('9.9.6')
if count < 4:
    raise SystemExit(f'expected at least 4 V9.9.6 markers, got {count}')
text = text.replace('9.9.6', '9.9.7')
text = text.replace('V9.3-P1 Spotify Core:', 'V9.9.7 Spotify Core:', 1)
ui.write_text(text, encoding='utf-8', newline='\n')
check = ui.read_text(encoding='utf-8')
assert 'Nghia Edition V9.9.7' in check
assert 'NGHIA_LOCAL_VERSION", "9.9.7"' in check
assert 'Nghia Edition V9.9.6' not in check
assert 'NGHIA_LOCAL_VERSION", "9.9.6"' not in check
assert 'LẤY TỌA ĐỘ / THÊM MAP' in check
assert 'command=self.show_coordinate_map_builder' in check
(root / 'version.json').write_text(json.dumps({'version': '9.9.7'}, indent=2) + '\n', encoding='utf-8')
ud = root / 'user_data'
ud.mkdir(exist_ok=True)
(ud / 'update_status.json').write_text(json.dumps({'latest_version': '9.9.7', 'local_version': '9.9.7', 'notes': 'V9.9.7 CoordinateMapBuilder Windows candidate', 'state': 'up_to_date'}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('V997_VERSION_PROMOTION_OK', count)
