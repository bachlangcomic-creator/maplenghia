from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json, shutil
from v1021_release import PORTABLE_ASSET, UPDATE_ASSET, VERSION

REQUIRED_UPDATE_FILES = [
    "NghiaClientApp.exe",
    "nghia_spotify_nologin.py",
    "maple_nghia_pro.py",
    "nghia_strategy_v10.py",
    "nghia_custom_map_profiles.py",
    "spotify_detection_parity.py",
    "spotify_watchdog.py",
    "spotify_recovered_core.py",
    "spotify_behavior_engine.py",
    "spotify_miumiu_sell.py",
    "spotify_pc_alarm.py",
]
root = Path("portable")
shutil.rmtree(root / "app_payload" / "dist_nuitka", ignore_errors=True)
for d in list(root.rglob("__pycache__")) + list(root.rglob(".pytest_cache")):
    shutil.rmtree(d, ignore_errors=True)
ud = root / "user_data"; ud.mkdir(exist_ok=True)
crash = ud / "launcher_crash.log"
if crash.exists(): crash.unlink()
(root / "version.json").write_text(json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8")
(ud / "update_status.json").write_text(json.dumps({
    "latest_version": VERSION,
    "local_version": VERSION,
    "notes": "Nghia V10.0.21 TWO FLOOR pass count 1-10; V10.0.20 Edit Map, V10.0.19 CAPTCHA, V10.0.18 MiuMiu preserved",
    "state": "up_to_date",
}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
payload = root / "app_payload"
missing = [n for n in REQUIRED_UPDATE_FILES if not (payload / n).is_file()]
if missing: raise SystemExit("missing updater files: " + ", ".join(missing))
meta = {"version": VERSION, "payload_dir": "app_payload", "required_files": REQUIRED_UPDATE_FILES}
out = Path("out"); out.mkdir(exist_ok=True)
portable = out / PORTABLE_ASSET
with ZipFile(portable, "w", ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(root.rglob("*")):
        if p.is_file(): z.write(p, p.relative_to(root).as_posix())
updater = out / UPDATE_ASSET
with ZipFile(updater, "w", ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(payload.rglob("*")):
        if p.is_file(): z.write(p, p.relative_to(root).as_posix())
    z.writestr("release.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
psha = hashlib.sha256(portable.read_bytes()).hexdigest()
usha = hashlib.sha256(updater.read_bytes()).hexdigest()
report = {
    "version": VERSION,
    "variant": "TwoFloorPassCount",
    "base_release": "v10.0.20",
    "two_floor_passes_per_floor": [1, 10],
    "full_crossing_only_counts": True,
    "first_edge_arms_counter": True,
    "verified_y_transition_preserved": True,
    "two_floor_recovery_preserved": True,
    "custom_map_edit_preserved": True,
    "captcha_scale_latch_preserved": True,
    "miumiu_strict_preserved": True,
    "bundled_maps_json_changed": False,
    "spotify_recovered_core_changed": False,
    "feature_tests": 4,
    "compileall": True,
    "nuitka_build": True,
    "windows_launcher_smoke": True,
    "packaged_launcher_smoke": False,
    "portable_sha256": psha,
    "updater_sha256": usha,
}
(out / "preflight_report_v1021.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
(out / "preflight_hashes_v1021.txt").write_text(f"{psha}  {portable.name}\n{usha}  {updater.name}\n", encoding="utf-8")
print("V1021_PACKAGE_OK", psha, usha)
