import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1] / "evidence" / "main_farm_worker.json"
ALLOWED = {"direct", "high_structural", "nghia_fallback"}


def test_main_farm_evidence_is_labeled_and_thread_order_unknown():
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["stage_order"]["value"] == [
        "state_gate",
        "sell_safe",
        "pet",
        "lost_player_recovery",
        "buff1",
        "buff2",
        "farm_dispatch",
    ]
    assert data["stage_order"]["evidence"] in ALLOWED
    assert data["ownership"]["evidence"] in ALLOWED
    assert all(v["evidence"] in ALLOWED for v in data["timing"].values())
    assert data["thread_start_order"] is None
