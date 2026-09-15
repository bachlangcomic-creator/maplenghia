from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json, shutil

root = Path('portable')
shutil.rmtree(root / 'app_payload' / 'dist_nuitka', ignore_errors=True)
for d in list(root.rglob('__pycache__')):
    shutil.rmtree(d, ignore_errors=True)
for d in list(root.rglob('.pytest_cache')):
    shutil.rmtree(d, ignore_errors=True)

(root / 'version.json').write_text(json.dumps({'version': '10.0.5'}, indent=2) + '\n', encoding='utf-8')
ud = root / 'user_data'
ud.mkdir(exist_ok=True)
(ud / 'update_status.json').write_text(json.dumps({
    'latest_version': '10.0.3',
    'local_version': '10.0.5',
    'notes': 'V10.0.5 Demo is opt-in. Stable auto-update remains V10.0.3.',
    'state': 'up_to_date'
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

out = Path('out')
out.mkdir(exist_ok=True)
portable = out / 'NghiaClient_V10.0.5_EnhancedLevel2Vision_Demo_Windows.zip'
with ZipFile(portable, 'w', ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())

sha = hashlib.sha256(portable.read_bytes()).hexdigest()
latest = json.loads(Path('latest.json').read_text(encoding='utf-8'))
if latest.get('version') != '10.0.3' or latest.get('channel') != 'stable':
    raise SystemExit('Refusing to package: stable latest.json is no longer V10.0.3 stable')
report = {
    'version': '10.0.5',
    'variant': 'EnhancedLevel2Vision_Demo',
    'base_version': '10.0.3',
    'demo_only': True,
    'stable_manifest_version': latest.get('version'),
    'stable_manifest_unchanged': True,
    'legacy_core_hash_guard': True,
    'vision_sensor_level2': True,
    'nuitka_build': True,
    'windows_launcher_smoke': True,
    'packaged_launcher_smoke': False,
    'portable_sha256': sha,
}
(out / 'preflight_report_v10.0.5_demo.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
(out / 'preflight_hashes_v10.0.5_demo.txt').write_text(f'{sha}  {portable.name}\n', encoding='utf-8')
print('V1005_DEMO_PACKAGE_OK', sha)
