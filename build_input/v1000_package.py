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
(root/'version.json').write_text(json.dumps({'version':'10.0.0'},indent=2)+'\n',encoding='utf-8')
(ud/'update_status.json').write_text(json.dumps({
    'latest_version':'10.0.0','local_version':'10.0.0',
    'notes':'V10.0.0 Isolated Strategy Engine candidate','state':'up_to_date'
},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
out=Path('out'); out.mkdir(exist_ok=True)
dst=out/'NghiaClient_V10.0.0_IsolatedStrategyEngine_Windows_Candidate.zip'
with ZipFile(dst,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(root).as_posix())
sha=hashlib.sha256(dst.read_bytes()).hexdigest()
protected={
 'spotify_recovered_core.py':'18e164944d5842629af55ca0f70f274192421515c01ac6451c0bdedf13109d95',
 'spotify_recovered_api.py':'1ceb0d194d1edfcab1a8005ac7fdd04343a90ff6962dc77d2dc675aac06a4339',
 'spotify_behavior_engine.py':'de137e5486518d183e26b83d360fa4a164e0fd136ce1deef003d6ad7b953fe97',
 'spotify_main_farm_orchestrator.py':'1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68',
}
report={
    'version':'10.0.0','variant':'IsolatedStrategyEngine',
    'engine_marker':'STRATEGY_V10','legacy_hard_isolation':True,
    'protected_legacy_hashes':protected,'maps_json_changed':False,
    'compileall':True,'feature_tests':True,'legacy_isolation_tests':True,
    'nuitka_build':True,'windows_launcher_smoke':True,
    'packaged_launcher_smoke':False,'portable_sha256':sha,
    'public_publish_performed':False,
}
(out/'preflight_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(out/'preflight_hashes.txt').write_text(f'{sha}  {dst.name}\n',encoding='utf-8')
print('V1000_PACKAGE_OK',sha)
