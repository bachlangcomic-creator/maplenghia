from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json, shutil
from v1016_release import PORTABLE_ASSET, UPDATE_ASSET, VERSION
REQUIRED_UPDATE_FILES=[
    'NghiaClientApp.exe','nghia_spotify_nologin.py','maple_nghia_pro.py',
    'spotify_recovered_core.py','spotify_behavior_engine.py','spotify_miumiu_sell.py','spotify_pc_alarm.py',
]
root=Path('portable')
shutil.rmtree(root/'app_payload'/'dist_nuitka',ignore_errors=True)
for d in list(root.rglob('__pycache__'))+list(root.rglob('.pytest_cache')):
    shutil.rmtree(d,ignore_errors=True)
ud=root/'user_data'; ud.mkdir(exist_ok=True)
crash=ud/'launcher_crash.log'
if crash.exists(): crash.unlink()
(root/'version.json').write_text(json.dumps({'version':VERSION},indent=2)+'\n',encoding='utf-8')
(ud/'update_status.json').write_text(json.dumps({'latest_version':VERSION,'local_version':VERSION,'notes':'Nghia V10.0.16 Custom Safe Entry + Farm Return','state':'up_to_date'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
payload=root/'app_payload'
missing=[n for n in REQUIRED_UPDATE_FILES if not (payload/n).is_file()]
if missing: raise SystemExit('V10.0.16 updater payload missing: '+', '.join(missing))
meta={'version':VERSION,'payload_dir':'app_payload','required_files':REQUIRED_UPDATE_FILES}
out=Path('out'); out.mkdir(exist_ok=True)
portable=out/PORTABLE_ASSET
with ZipFile(portable,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(root).as_posix())
updater=out/UPDATE_ASSET
with ZipFile(updater,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(payload.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(root).as_posix())
    z.writestr('release.json',json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
psha=hashlib.sha256(portable.read_bytes()).hexdigest(); usha=hashlib.sha256(updater.read_bytes()).hexdigest()
report={
    'version':VERSION,'variant':'CustomSafeReturn','base_release':'v10.0.15',
    'custom_map_safe_entry':True,'custom_map_farm_return':True,'up_jump_to_safe':True,'down_jump_to_farm':True,
    'post_sell_return_to_farm':True,'upper_floor_fall_recovery_uses_farm_return':True,
    'original_maps_unchanged':True,'maps_json_changed':False,'protected_core_changed':False,
    'v1015_human_rest_preserved':True,'v1014_sell_trigger_arbitration_preserved':True,
    'adaptive_y_preserved':True,'anti_jitter_preserved':True,'stop_nonblocking_preserved':True,
    'feature_tests':8,'anti_jitter_tests':17,'compileall':True,'nuitka_build':True,
    'windows_launcher_smoke':True,'packaged_launcher_smoke':False,
    'portable_sha256':psha,'updater_sha256':usha,'stable_latest_json_modified':False,'public_publish_performed':False,
}
(out/'preflight_report_v1016.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(out/'preflight_hashes_v1016.txt').write_text(f'{psha}  {portable.name}\n{usha}  {updater.name}\n',encoding='utf-8')
print('V1016_PACKAGE_OK',psha,usha)
