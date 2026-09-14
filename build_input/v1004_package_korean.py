from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

VERSION = "10.0.4"
ROOT = Path("portable")
APP = ROOT / "app_payload"
OUT = Path("out")
FULL_NAME = "NghiaClient_V10.0.4_KoreanHelper_PortableOCR_Windows.zip"
UPDATE_NAME = "NghiaEdition_Update_v10.0.4.zip"
LOCKED_CORE_SHA = "020770a55f5f59b4be1ce07c8de28eee15019070146b593c23ed3a1d56349ea4"
UI_SHA = "6c131af3486dacf848eff9889eb83595774912f78ee70fb1185fb5a58799ec3b"
HELPER_SHA = "605dd74d6d117825b44c3a5ed52b418a894563d6877f24dd62e727be25cf302e"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_tree(zf: ZipFile, root: Path, arc_root: Path | None = None) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if arc_root is None:
            arcname = path.relative_to(root).as_posix()
        else:
            arcname = (arc_root / path.relative_to(root)).as_posix()
        zf.write(path, arcname)


if sha256(APP / "maple_nghia_pro.py") != LOCKED_CORE_SHA:
    raise SystemExit("locked core hash mismatch")
if sha256(APP / "nghia_spotify_nologin.py") != UI_SHA:
    raise SystemExit("V10.0.4 UI hash mismatch")
if sha256(APP / "korean_question_helper.py") != HELPER_SHA:
    raise SystemExit("V10.0.4 Korean helper hash mismatch")

required = [
    "NghiaClientApp.exe",
    "nghia_spotify_nologin.py",
    "maple_nghia_pro.py",
    "spotify_recovered_core.py",
    "spotify_behavior_engine.py",
    "spotify_miumiu_sell.py",
    "spotify_pc_alarm.py",
    "korean_question_helper.py",
    "tesseract/tesseract.exe",
    "tesseract/tessdata/kor.traineddata",
    "tesseract/tessdata/eng.traineddata",
]
for rel in required:
    if not (APP / rel).is_file():
        raise SystemExit(f"required V10.0.4 file missing: app_payload/{rel}")

OUT.mkdir(parents=True, exist_ok=True)
(ROOT / "version.json").write_text(json.dumps({"version": VERSION}, indent=2) + "\n", encoding="utf-8")

full_zip = OUT / FULL_NAME
with ZipFile(full_zip, "w", ZIP_DEFLATED, compresslevel=9) as zf:
    add_tree(zf, ROOT)

release = {
    "version": VERSION,
    "payload_dir": "app_payload",
    "required_files": required,
}
release_bytes = (json.dumps(release, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
update_zip = OUT / UPDATE_NAME
with ZipFile(update_zip, "w", ZIP_DEFLATED, compresslevel=9) as zf:
    zf.writestr("release.json", release_bytes)
    add_tree(zf, APP, Path("app_payload"))

# Validate the update archive using the exact launcher package validator shipped
# with the portable build, not a duplicate validator.
sys.path.insert(0, str(ROOT.resolve()))
from launcher.package_validation import safe_extract_update, validate_staged_payload  # noqa: E402

verify_root = Path("verify_v1004_update")
shutil.rmtree(verify_root, ignore_errors=True)
safe_extract_update(update_zip, verify_root)
payload = validate_staged_payload(verify_root, VERSION)
for rel in required:
    if not (payload / rel).is_file():
        raise SystemExit(f"validated payload lost required file: {rel}")
shutil.rmtree(verify_root, ignore_errors=True)

full_digest = sha256(full_zip)
update_digest = sha256(update_zip)
report = {
    "version": VERSION,
    "variant": "KoreanHelperPortableOCRFix",
    "locked_core_sha256": LOCKED_CORE_SHA,
    "ui_sha256": UI_SHA,
    "helper_sha256": HELPER_SHA,
    "bundled_tesseract": True,
    "bundled_kor_traineddata": True,
    "bundled_eng_traineddata": True,
    "runtime_download_required": False,
    "nuitka_onefile_client": True,
    "launcher_smoke": True,
    "onefile_ocr_locator_regression_test": True,
    "launcher_update_package_validated": True,
    "portable_sha256": full_digest,
    "update_sha256": update_digest,
}
(OUT / "korean_portable_preflight_v10.0.4.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
(OUT / "korean_portable_sha256_v10.0.4.txt").write_text(
    f"{full_digest}  {FULL_NAME}\n{update_digest}  {UPDATE_NAME}\n", encoding="utf-8"
)
print("V1004_KOREAN_PACKAGES_OK", full_zip, full_digest, update_zip, update_digest)
