import ast
import os
from pathlib import Path

APP = Path(os.environ["APP_PAYLOAD"])


def fn(name):
    text = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_safe_place_ready_dispatches_without_marking_sell_complete():
    src = fn("_spotify_mainfarm_sell_safe_stage")
    start = src.index('if safe_outcome == "READY":')
    end = src.index('elif safe_outcome == "FAILED":', start)
    ready = src[start:end]
    assert "run_sell_thread(cfg)" in ready
    assert "notify_sell_completed" not in ready
    assert "not self.spotify_sell_inflight" in ready
    assert ready.index("self.spotify_sell_inflight = True") < ready.index("run_sell_thread(cfg)")


def test_sell_inflight_is_initialized_and_reset_at_start_stop():
    assert "self.spotify_sell_inflight = False" in fn("__init__")
    assert "self.spotify_sell_inflight = False" in fn("start_bot")
    assert "self.spotify_sell_inflight = False" in fn("stop_bot")


def test_worker_uses_real_miumiu_ok_as_completion_signal():
    src = fn("_sell_sequence_worker")
    assert "ok = self.miumiu_seller.run" in src
    success = src[src.index("if ok:") :]
    assert "spotify_watchdog.notify_sell_completed" in success
    assert success.index("if ok:") < success.index("spotify_watchdog.notify_sell_completed")
    assert "spotify_sell_timer_event.clear()" in success
    assert "spotify_sell_inflight = False" in success


def test_worker_failure_rearms_pending_timer_without_false_completion():
    src = fn("_sell_sequence_worker")
    assert "if self.running and (self.runtime_cfg or cfg).get(\"auto_sell_timer_enabled\")" in src
    assert "spotify_sell_timer_event.set()" in src
    failure = src[src.rindex("else:") :]
    assert "spotify_sell_inflight = False" in failure
    assert "spotify_sell_timer_event.set()" in failure
    assert "notify_sell_completed" not in failure


def test_worker_exception_path_rearms_without_false_completion():
    src = fn("_sell_sequence_worker")
    assert "except Exception" in src
    except_slice = src[src.index("except Exception") : src.index("if ok:")]
    assert "spotify_sell_inflight = False" in except_slice
    assert "spotify_sell_timer_event.set()" in except_slice
    assert "notify_sell_completed" not in except_slice
