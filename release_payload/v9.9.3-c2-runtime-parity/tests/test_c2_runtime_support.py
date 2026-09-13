import os
import sys
from pathlib import Path

APP_PAYLOAD = Path(os.environ["APP_PAYLOAD"])
sys.path.insert(0, str(APP_PAYLOAD))


def test_pause_reasons_compose_without_early_resume():
    from spotify_c2_runtime_support import C2PauseReasons
    gate = C2PauseReasons()
    gate.add("sell")
    gate.add("captcha")
    assert gate.blocked() is True
    assert gate.snapshot() == ("captcha", "sell")
    gate.remove("sell")
    assert gate.blocked() is True
    assert gate.snapshot() == ("captcha",)
    gate.remove("captcha")
    assert gate.blocked() is False
    assert gate.snapshot() == ()


def test_trace_buffer_is_disabled_by_default_and_uses_monotonic_ns(tmp_path):
    from spotify_c2_runtime_support import C2RuntimeTraceBuffer
    trace = C2RuntimeTraceBuffer(enabled=False)
    trace.emit("combo_start", map="C2")
    assert trace.snapshot() == []
    trace = C2RuntimeTraceBuffer(enabled=True)
    trace.emit("combo_start", map="C2")
    rows = trace.snapshot()
    assert len(rows) == 1
    assert rows[0]["event"] == "combo_start"
    assert rows[0]["map"] == "C2"
    assert isinstance(rows[0]["t_ns"], int)
    out = tmp_path / "trace.jsonl"
    trace.dump(out)
    assert '"event": "combo_start"' in out.read_text(encoding="utf-8")


def test_legacy_c2_pause_boolean_is_removed():
    source = (APP_PAYLOAD / "maple_nghia_pro.py").read_text(encoding="utf-8")
    assert "c2_fast_supervisor_pause" not in source
    for reason in ("sell", "captcha", "disconnect", "revive", "all_cure", "stop"):
        assert f'"{reason}"' in source
