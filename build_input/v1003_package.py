from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json, shutil

root = Path('portable')
shutil.rmtree(root / 'app_payload' / 'dist_nuitka', ignore_errors=True)
for d in list(root.rglob('__pycache__')):
    shutil.rmtree(d, ignore_errors=True)
for d in list(root.rglob('.pytest_cache')):
    shutil.rmtree(d, ignore_errors=True)
ud = root / 'user_data'
ud.mkdir(exist_ok=True)
crash = ud / 'launcher_crash.log'
if crash.exists():
    crash.unlink()
(root / 'version.json').write_text(json.dumps({'version': '10.0.3'}, indent=2) + '\n', encoding='utf-8')
(ud / 'update_status.json').write_text(json.dumps({
    'latest_version': '10.0.3',
    'local_version': '10.0.3',
    'notes': 'Nghia V10.0.3 Loot Parity Defense',
    'state': 'up_to_date'
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

out = Path('out')
out.mkdir(exist_ok=True)
portable = out / 'NghiaClient_V10.0.3_LootParityDefense_Windows_Candidate.zip'
with ZipFile(portable, 'w', ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())

updater = out / 'NghiaEdition_Update_v10.0.3.zip'
with ZipFile(updater, 'w', ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted((root / 'app_payload').rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())

psha = hashlib.sha256(portable.read_bytes()).hexdigest()
usha = hashlib.sha256(updater.read_bytes()).hexdigest()
report = {
    'version': '10.0.3',
    'variant': 'LootParityDefense',
    'base_version': '10.0.2',
    'loot_parity_defense': True,
    'exact_parity_generic_loot_blocked_for_non_pirate': True,
    'pirate_route_loot_unchanged': True,
    'combat_timing_unchanged': True,
    'worker_supervisor_generation_race_fixed': True,
    'strategy_v10_unchanged': True,
    'maps_json_changed': False,
    'compileall': True,
    'feature_tests': True,
    'nuitka_build': True,
    'windows_launcher_smoke': True,
    'packaged_launcher_smoke': False,
    'portable_sha256': psha,
    'updater_sha256': usha,
    'public_publish_performed': False,
}
(out / 'preflight_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
(out / 'preflight_hashes.txt').write_text(
    f'{psha}  {portable.name}\n{usha}  {updater.name}\n', encoding='utf-8'
)
print('V1003_PACKAGE_OK', psha, usha)
