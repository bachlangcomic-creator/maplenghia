import os
import re
from pathlib import Path

APP_PAYLOAD = Path(os.environ["APP_PAYLOAD"])


def function_body(source: str, name: str) -> str:
    start = source.index(f"    def {name}")
    match = re.search(r"^    def ", source[start + 5 :], re.M)
    return source[start:] if not match else source[start : start + 5 + match.start()]


def test_existing_c2_helper_has_runtime_supported_timing_family():
    source = (APP_PAYLOAD / "spotify_recovered_core.py").read_text(encoding="utf-8")
    body = function_body(source, "_spotify_c2_tp_skill_hold_combo")
    assert "SPOTIFY_R54_COMBO_SPAM_ACTION_MS" in body
    assert "SPOTIFY_R54_COMBO_SPAM_WAIT_S" in body
    assert "random.randint" in body
    assert "random.uniform" in body


def test_primary_skill_step_routes_only_c2_to_c2_runtime_helper():
    source = (APP_PAYLOAD / "spotify_recovered_core.py").read_text(encoding="utf-8")
    body = function_body(source, "_spotify_primary_skill_step")
    assert 'current_map' in body
    assert '"C2"' in body
    assert "_spotify_c2_tp_skill_hold_combo" in body
    assert "_spotify_hold_combo_action" in body
    assert "SPOTIFY_SIMPLE_PRE_COMBO_SLEEP" in body
    assert "SPOTIFY_SIMPLE_HOLD_COMBO_MS" in body
