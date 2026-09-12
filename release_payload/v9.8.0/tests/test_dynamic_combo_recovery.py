import json
import os
from pathlib import Path

APP = Path(os.environ.get("APP_PAYLOAD", Path(__file__).resolve().parents[3]))
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence" / "dynamic_combo_callers.json"


def _app_text():
    return "\n".join((APP / n).read_text(encoding="utf-8") for n in (
        "maple_nghia_pro.py", "spotify_behavior_engine.py", "spotify_recovered_core.py"
    ))


def test_dynamic_combo_caller_fixture_controls_runtime_wiring():
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    text = _app_text()
    callers = data["callers"]
    if not callers:
        assert text.count("_spotify_dynamic_combo_reconstructed(") == 1
    else:
        assert text.count("_spotify_dynamic_combo_reconstructed(") == 1 + len(callers)


def test_c2_never_routes_through_generic_dynamic_combo():
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8").lower()
    start = text.index("def _c2_fast_farm_worker")
    end = text.find("\n    def ", start + 10)
    src = text[start:end if end > start else None]
    assert "dynamic_combo" not in src
