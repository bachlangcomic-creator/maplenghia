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
FINAL_UI_SHA = "43c4935952966297be4ed71cc159d744e3177ccc26a0e8027ff1f68350955ab1"
HELPER_SHA = "94e422ca8a48d3133bd42cce064fb4beee59af27740b668dfc90f147fbcca0d5"
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
    raise SystemExit(f"unexpected V10.0.3 UI: {sha(UI)}")
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

print("V1003_KOREAN_PORTABLE_APPLY_OK")
