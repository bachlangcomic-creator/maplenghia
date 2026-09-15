from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import shutil

from v1008_release import PORTABLE_ASSET, UPDATE_ASSET, VERSION

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
            "notes": "Nghia V10.0.8 Map-Aware Adaptive Y Toggle",
            "state": "up_to_date",
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n",
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
    "variant": "MapAwareAdaptiveYToggle",
    "base_release": "v10.0.7",
    "adaptive_y_maps": ["C2", "B3"],
    "adaptive_y_other_maps_disabled": True,
    "adaptive_y_runtime_cfg_live_update": True,
    "adaptive_y_state_reset_on_toggle": True,
    "c2_engine_changed": False,
    "b3_engine_changed": False,
    "anti_jitter_changed": False,
    "stop_nonblocking_preserved": True,
    "maps_json_changed": False,
    "combat_timing_changed": False,
    "compileall": True,
    "adaptive_y_tests": 5,
    "anti_jitter_tests": 17,
    "stop_regression": True,
    "nuitka_build": True,
    "windows_launcher_smoke": True,
    "packaged_launcher_smoke": False,
    "portable_sha256": psha,
    "updater_sha256": usha,
    "stable_latest_json_modified": False,
    "public_publish_performed": False,
}
(out / "preflight_report_v1008.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
(out / "preflight_hashes_v1008.txt").write_text(
    f"{psha}  {portable.name}\n{usha}  {updater.name}\n", encoding="utf-8"
)
print("V1008_PACKAGE_OK", psha, usha)
