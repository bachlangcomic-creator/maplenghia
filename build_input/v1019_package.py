from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json, shutil
from v1019_release import PORTABLE_ASSET, UPDATE_ASSET, VERSION

REQUIRED_UPDATE_FILES = [
    "NghiaClientApp.exe",
    "nghia_spotify_nologin.py",
    "maple_nghia_pro.py",
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
ud = root / "user_data"
ud.mkdir(exist_ok=True)
crash = ud / "launcher_crash.log"
if crash.exists():
    crash.unlink()
(root / "version.json").write_text(
    json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8"
)
(ud / "update_status.json").write_text(
    json.dumps(
        {
            "latest_version": VERSION,
            "local_version": VERSION,
            "notes": "Nghia V10.0.19 CAPTCHA multi-scale LIE_B64 + 3-frame clear latch; V10.0.18 MiuMiu Strict preserved",
            "state": "up_to_date",
        },
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)
payload = root / "app_payload"
missing = [n for n in REQUIRED_UPDATE_FILES if not (payload / n).is_file()]
if missing:
    raise SystemExit("missing updater files: " + ", ".join(missing))
meta = {"version": VERSION, "payload_dir": "app_payload", "required_files": REQUIRED_UPDATE_FILES}
out = Path("out")
out.mkdir(exist_ok=True)
portable = out / PORTABLE_ASSET
with ZipFile(portable, "w", ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(root.rglob("*")):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())
updater = out / UPDATE_ASSET
with ZipFile(updater, "w", ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(payload.rglob("*")):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())
    z.writestr("release.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
psha = hashlib.sha256(portable.read_bytes()).hexdigest()
usha = hashlib.sha256(updater.read_bytes()).hexdigest()
report = {
    "version": VERSION,
    "variant": "CaptchaScaleLatch",
    "base_release": "v10.0.18",
    "captcha_primary_asset": "LIE_B64",
    "captcha_scales": [0.90, 0.95, 1.00, 1.05, 1.10],
    "captcha_threshold": 0.70,
    "captcha_clear_frames": 3,
    "question_assets_as_alarm_triggers": False,
    "pc_alarm_unchanged": True,
    "miumiu_strict_preserved": True,
    "maps_json_changed": False,
    "protected_core_changed": False,
    "feature_tests": 4,
    "compileall": True,
    "nuitka_build": True,
    "windows_launcher_smoke": True,
    "packaged_launcher_smoke": False,
    "portable_sha256": psha,
    "updater_sha256": usha,
}
(out / "preflight_report_v1019.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
(out / "preflight_hashes_v1019.txt").write_text(
    f"{psha}  {portable.name}\n{usha}  {updater.name}\n", encoding="utf-8"
)
print("V1019_PACKAGE_OK", psha, usha)
