from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json, shutil

root=Path('portable')
shutil.rmtree(root/'app_payload'/'dist_nuitka',ignore_errors=True)
for d in list(root.rglob('__pycache__')): shutil.rmtree(d,ignore_errors=True)
for d in list(root.rglob('.pytest_cache')): shutil.rmtree(d,ignore_errors=True)
ud=root/'user_data'; ud.mkdir(exist_ok=True)
crash=ud/'launcher_crash.log'
if crash.exists(): crash.unlink()
(root/'version.json').write_text(json.dumps({'version':'9.9.8'},indent=2)+'\n',encoding='utf-8')
(ud/'update_status.json').write_text(json.dumps({
    'latest_version':'9.9.8','local_version':'9.9.8',
    'notes':'V9.9.8 Pirate Points MapBuilder candidate','state':'up_to_date'
},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
out=Path('out'); out.mkdir(exist_ok=True)
dst=out/'NghiaClient_V9.9.8_PiratePointsMapBuilder_Windows_Candidate.zip'
with ZipFile(dst,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(root).as_posix())
sha=hashlib.sha256(dst.read_bytes()).hexdigest()
report={
    'version':'9.9.8','variant':'PiratePointsMapBuilder',
    'feature_scope':'capture_and_save_only',
    'pirate_fields':['LEFT','RIGHT','SAFE','LOOT_BOT_LEFT','LOOT_BOT_RIGHT','LOOT_BOT_1','LOOT_BOT_2'],
    'engine_route_changed':False,'maps_json_changed':False,
    'compileall':True,'feature_tests':True,'nuitka_build':True,
    'windows_launcher_smoke':True,'packaged_launcher_smoke':False,
    'portable_sha256':sha,'public_publish_performed':False,
}
(out/'preflight_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(out/'preflight_hashes.txt').write_text(f'{sha}  {dst.name}\n',encoding='utf-8')
print('V998_PACKAGE_OK',sha)
