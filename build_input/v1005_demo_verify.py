from pathlib import Path
import hashlib, json, subprocess, sys

ROOT = Path('.')
PORTABLE = ROOT / 'portable'
APP = PORTABLE / 'app_payload'

LEGACY = {
    'spotify_recovered_core.py': '5d0219ea9129a9e5362f4e8a8eb072dd6f8a927dd9ba71db24eaa414afa45c3e',
    'spotify_behavior_engine.py': 'de137e5486518d183e26b83d360fa4a164e0fd136ce1deef003d6ad7b953fe97',
    'nghia_strategy_v10.py': '6066d1ec948b7e9783944a1c2825a033061b1e130fde44b3799783263b1da9b8',
}

def fail(msg):
    raise SystemExit(msg)

latest = json.loads((ROOT / 'latest.json').read_text(encoding='utf-8'))
if latest.get('version') != '10.0.3' or latest.get('channel') != 'stable':
    fail(f"stable latest.json changed unexpectedly: {latest}")

version = json.loads((PORTABLE / 'version.json').read_text(encoding='utf-8'))
if version.get('version') != '10.0.5':
    fail(f"demo version mismatch: {version}")

for name, expected in LEGACY.items():
    got = hashlib.sha256((APP / name).read_bytes()).hexdigest()
    if got != expected:
        fail(f'legacy source changed: {name} {got}')

for name in ('nghia_enhanced_engine.py', 'nghia_enhanced_sensor.py'):
    if not (APP / name).is_file():
        fail(f'missing enhanced module: {name}')

ui = (APP / 'nghia_spotify_nologin.py').read_text(encoding='utf-8')
for needle in ('Nghia Edition V10.0.5 Demo', 'CẤU HÌNH VISION SENSOR', '_enhanced_map_block'):
    if needle not in ui:
        fail(f'missing UI marker: {needle}')

subprocess.run([sys.executable, '-m', 'compileall', '-q', str(APP)], check=True)
subprocess.run([sys.executable, '-m', 'pytest', '-q', str(PORTABLE / 'tests')], check=True)
print('V1005_DEMO_VERIFY_OK')
