from pathlib import Path
import base64
import hashlib
import zlib

ROOT = Path("portable")
APP = ROOT / "app_payload"
PAYLOAD = Path("build_input/korean_payload")
UI = APP / "nghia_spotify_nologin.py"
CORE = APP / "maple_nghia_pro.py"
HELPER = APP / "korean_question_helper.py"
REQ = APP / "requirements.txt"

BASE_UI_SHA = "61131ccedd816af3c375f583b4e806b620abcaf7c9a866e158e5c059e7ab03bd"
LOCKED_CORE_SHA = "020770a55f5f59b4be1ce07c8de28eee15019070146b593c23ed3a1d56349ea4"
FINAL_UI_SHA = "6c131af3486dacf848eff9889eb83595774912f78ee70fb1185fb5a58799ec3b"
HELPER_SHA = "605dd74d6d117825b44c3a5ed52b418a894563d6877f24dd62e727be25cf302e"
REQ_SHA = "f0cf9eafb68704e1000b1e567b04252374ea6355c09b08decc49cfa67263498c"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_parts(prefix: str) -> bytes:
    parts = sorted(PAYLOAD.glob(f"{prefix}.*.txt"))
    if not parts:
        raise SystemExit(f"missing Korean payload: {prefix}")
    encoded = "".join(p.read_text(encoding="ascii").strip() for p in parts)
    try:
        return zlib.decompress(base64.b64decode(encoded, validate=True))
    except Exception as exc:
        raise SystemExit(f"invalid Korean payload {prefix}: {exc}") from exc


if sha(UI) != BASE_UI_SHA:
    raise SystemExit(f"unexpected V10.0.3 baseline UI: {sha(UI)}")
if sha(CORE) != LOCKED_CORE_SHA:
    raise SystemExit(f"locked core changed before Korean helper: {sha(CORE)}")

UI.write_bytes(decode_parts("ui"))
HELPER.write_bytes(decode_parts("helper"))
REQ.write_bytes(decode_parts("req"))

if sha(CORE) != LOCKED_CORE_SHA:
    raise SystemExit(f"locked core changed after Korean helper: {sha(CORE)}")
if sha(UI) != FINAL_UI_SHA:
    raise SystemExit(f"Korean helper UI hash mismatch: {sha(UI)}")
if sha(HELPER) != HELPER_SHA:
    raise SystemExit(f"Korean helper hash mismatch: {sha(HELPER)}")
if sha(REQ) != REQ_SHA:
    raise SystemExit(f"requirements hash mismatch: {sha(REQ)}")
if b"pytesseract" not in REQ.read_bytes():
    raise SystemExit("pytesseract missing from requirements")

print("V1004_KOREAN_OCR_FIX_APPLY_OK")
