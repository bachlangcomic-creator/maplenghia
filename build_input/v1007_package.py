from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import shutil

from v1007_release import PORTABLE_ASSET, UPDATE_ASSET, VERSION

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

(root / "version.json").write_text(
    json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8"
)
(ud / "update_status.json").write_text(
    json.dumps(
        {
            "latest_version": VERSION,
            "local_version": VERSION,
            "notes": "Nghia V10.0.7 Anti-Jitter / Hysteresis stable",
            "state": "up_to_date",
        },
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)

out = Path("out")
out.mkdir(exist_ok=True)
portable = out / PORTABLE_ASSET
with ZipFile(portable, "w", ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(root.rglob("*")):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())

updater = out / UPDATE_ASSET
with ZipFile(updater, "w", ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted((root / "app_payload").rglob("*")):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())

psha = hashlib.sha256(portable.read_bytes()).hexdigest()
usha = hashlib.sha256(updater.read_bytes()).hexdigest()
report = {
    "version": VERSION,
    "variant": "AntiJitterHysteresisStable",
    "base_release": "v10.0.6-antijitter",
    "semantic_version_only": True,
    "anti_jitter_default": False,
    "anti_jitter_confirm_frames": 2,
    "anti_jitter_lock_seconds": 0.40,
    "anti_jitter_departure_pixels": 8.0,
    "anti_jitter_owns_input": False,
    "stop_nonblocking_preserved": True,
    "maps_json_changed": False,
    "logic_hashes_unchanged": True,
    "compileall": True,
    "release_metadata_tests": True,
    "feature_tests": 17,
    "stop_regression": True,
    "nuitka_build": True,
    "windows_launcher_smoke": True,
    "packaged_launcher_smoke": False,
    "portable_sha256": psha,
    "updater_sha256": usha,
    "stable_latest_json_modified": False,
    "public_publish_performed": False,
}
(out / "preflight_report_v1007.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
(out / "preflight_hashes_v1007.txt").write_text(
    f"{psha}  {portable.name}\n{usha}  {updater.name}\n", encoding="utf-8"
)
print("V1007_PACKAGE_OK", psha, usha)
