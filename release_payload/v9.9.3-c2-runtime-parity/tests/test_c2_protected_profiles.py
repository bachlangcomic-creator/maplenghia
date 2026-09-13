import hashlib
import os
from pathlib import Path

APP_PAYLOAD = Path(os.environ["APP_PAYLOAD"])
PROTECTED = {
    "spotify_behavior_engine.py": "de137e5486518d183e26b83d360fa4a164e0fd136ce1deef003d6ad7b953fe97",
    "spotify_recovered_api.py": "1ceb0d194d1edfcab1a8005ac7fdd04343a90ff6962dc77d2dc675aac06a4339",
    "spotify_timing_catalog.py": "b1eab666bc1227fbb420695ffcdc5ea97dde6880a49cc15b42b88aa1633c1066",
    "spotify_focus_parity.py": "987774bdca786302001a0145474761986a0e8f9539b7f277157b40bf5b6fb9d1",
    "maps.json": "52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_protected_files_are_byte_identical():
    for name, expected in PROTECTED.items():
        assert sha(APP_PAYLOAD / name) == expected


def test_dynamic_combo_remains_out_of_active_dispatch():
    behavior = (APP_PAYLOAD / "spotify_behavior_engine.py").read_text(encoding="utf-8")
    assert "perform_dynamic_combo" not in behavior


def test_pirate_and_non_c2_shared_helper_contract_stays_present():
    core = (APP_PAYLOAD / "spotify_recovered_core.py").read_text(encoding="utf-8")
    assert "_spotify_hold_combo_action" in core
    assert "_spotify_pirate_step" in core
