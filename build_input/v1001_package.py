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
(root/'version.json').write_text(json.dumps({'version':'10.0.1'},indent=2)+'\n',encoding='utf-8')
(ud/'update_status.json').write_text(json.dumps({
    'latest_version':'10.0.1','local_version':'10.0.1',
    'notes':'V10.0.1 Spotify Stability candidate','state':'up_to_date'
},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
out=Path('out'); out.mkdir(exist_ok=True)
dst=out/'NghiaClient_V10.0.1_SpotifyStability_Windows_Candidate.zip'
with ZipFile(dst,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(root).as_posix())
sha=hashlib.sha256(dst.read_bytes()).hexdigest()
report={
    'version':'10.0.1','variant':'SpotifyStabilityParity',
    'lost_position_arbitration':'spotify_3s_stage_then_hard_4.5s_fallback',
    'c2_y_policy':'preserved_from_v10.0.0_adaptive_default_on',
    'b3_y_policy':'preserved_from_v10.0.0_existing_toggle_default_off',
    'strategy_v10_unchanged':True,
    'strategy_v10_sha256':'6066d1ec948b7e9783944a1c2825a033061b1e130fde44b3799783263b1da9b8',
    'maps_json_changed':False,
    'maps_json_sha256':'52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d',
    'compileall':True,'feature_tests':True,'legacy_stability_tests':True,
    'nuitka_build':True,'windows_launcher_smoke':True,
    'packaged_launcher_smoke':False,'portable_sha256':sha,
    'public_publish_performed':False,
}
(out/'preflight_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(out/'preflight_hashes.txt').write_text(f'{sha}  {dst.name}\n',encoding='utf-8')
print('V1001_PACKAGE_OK',sha)
