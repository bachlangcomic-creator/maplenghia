import hashlib
import os
from pathlib import Path

APP = Path(os.environ.get("V97_BASE_PAYLOAD", os.environ.get("APP_PAYLOAD", "/mnt/data/v97_public_final/app_payload")))
EXPECTED_RAW = {
    "maple_nghia_pro.py": "aa1b14d74b6bbacd91d6c8dc18ebb8fdc462b3df345ded5a9338b47f7601433d",
    "spotify_recovered_core.py": "5f3ba4dfa9886d75b80d39aca29e79ab500435e25e8dc592bc9423050d15675d",
    "spotify_behavior_engine.py": "4ed97d1eb1ff2ef3758fc243da600155fada71701f24b63b832fdc675cf84f08",
}
EXPECTED_NORMALIZED = {
    "maple_nghia_pro.py": "fe7821832fe4e4a6d163c69163d2dbddf5578c6030919a3014e64a355f3d3194",
    "spotify_recovered_core.py": "eaf052e9891a018c43f8dd51fb992ea75525855859754f73112fccbf46217aed",
    "spotify_behavior_engine.py": "3a6cc1e9ffaaae036c8625706aead23f5f85305a1a9de1165167240c9cae89db",
}


def test_public_v97_source_hashes_are_locked_before_overlay():
    for name, want in EXPECTED_RAW.items():
        got = hashlib.sha256((APP / name).read_bytes()).hexdigest()
        assert got == want, f"{name}: {got} != {want}"


def test_public_v97_normalizes_to_the_reviewed_lf_baseline():
    for name, want in EXPECTED_NORMALIZED.items():
        raw = (APP / name).read_bytes().replace(b"\r\n", b"\n")
        got = hashlib.sha256(raw).hexdigest()
        assert got == want, f"{name} normalized: {got} != {want}"
