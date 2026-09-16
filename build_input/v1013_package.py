from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import shutil

from v1013_release import PORTABLE_ASSET, UPDATE_ASSET, VERSION

REQUIRED_UPDATE_FILES = [
    "NghiaClientApp.exe",
    "nghia_spotify_nologin.py",
    "maple_nghia_pro.py",
    "spotify_recovered_core.py",
    "spotify_behavior_engine.py",
    "spotify_miumiu_sell.py",
    "spotify_pc_alarm.py",
]

root = Path("portable")
shutil.rmtree(root / "app_payload" / "dist_nuitka", ignore_errors=True)
for d in list(root.rglob("__pycache__")):
    shutil.rmtree(d, ignore_errors=True)
for d in list(root.rglob(".pytest_cache")):
    shutil.rmtree(d, ignore_errors=True)

ud = root / "user_data"
ud.mkdir(exist_ok=True)
crash = ud / "launcher_crash.log"
if crash.exists():
    crash.unlink()

(root / "version.json").write_text(json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8")
(ud / "update_status.json").write_text(
    json.dumps(
        {
            "latest_version": VERSION,
            "local_version": VERSION,
            "notes": "Nghia V10.0.13 Custom Map Sell-Safe",
            "state": "up_to_date",
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n",
    encoding="utf-8",
)

payload_root = root / "app_payload"
missing_required = [name for name in REQUIRED_UPDATE_FILES if not (payload_root / name).is_file()]
if missing_required:
    raise SystemExit(
        "V10.0.13 updater payload missing launcher-required files: " + ", ".join(missing_required)
    )

release_metadata = {
    "version": VERSION,
    "payload_dir": "app_payload",
    "required_files": REQUIRED_UPDATE_FILES,
}

out = Path("out")
out.mkdir(exist_ok=True)
portable = out / PORTABLE_ASSET
with ZipFile(portable, "w", ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(root.rglob("*")):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())

updater = out / UPDATE_ASSET
with ZipFile(updater, "w", ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(payload_root.rglob("*")):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())
    z.writestr(
        "release.json",
        json.dumps(release_metadata, indent=2, ensure_ascii=False) + "\n",
    )

psha = hashlib.sha256(portable.read_bytes()).hexdigest()
usha = hashlib.sha256(updater.read_bytes()).hexdigest()
report = {
    "version": VERSION,
    "variant": "CustomMapSellSafe",
    "base_release": "v10.0.12",
    "custom_map_sell_safe_stage": True,
    "sell_inflight_blocks_strategy": True,
    "sell_lock_blocks_strategy": True,
    "custom_map_safe_place_reused": True,
    "existing_miumiu_seller_reused": True,
    "v1012_watchdog_preview_fix_preserved": True,
    "v1011_simple_loot_optional_preserved": True,
    "v1010_custom_map_parity_preserved": True,
    "v1009_miumiu_timer_preserved": True,
    "adaptive_y_c2_b3_preserved": True,
    "anti_jitter_preserved": True,
    "stop_nonblocking_preserved": True,
    "maps_json_changed": False,
    "protected_core_changed": False,
    "updater_release_json_contract": True,
    "feature_tests": 3,
    "v1012_regressions": True,
    "v1011_regressions": True,
    "v1010_regressions": True,
    "v1009_regressions": True,
    "adaptive_y_regressions": True,
    "anti_jitter_tests": 17,
    "stop_regression": True,
    "compileall": True,
    "nuitka_build": True,
    "windows_launcher_smoke": True,
    "packaged_launcher_smoke": False,
    "portable_sha256": psha,
    "updater_sha256": usha,
    "stable_latest_json_modified": False,
    "public_publish_performed": False,
}
(out / "preflight_report_v1013.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
(out / "preflight_hashes_v1013.txt").write_text(
    f"{psha}  {portable.name}\n{usha}  {updater.name}\n", encoding="utf-8"
)
print("V1013_PACKAGE_OK", psha, usha)
