# Nghia V9.9.3 C2 Runtime Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a private V9.9.3 candidate that makes C2 runtime behavior measurably closer to Spotify by wiring the existing 20–50 ms / 50–150 ms C2 combo candidate, making the C2 minimap worker the sole main-farm owner, replacing the shared pause boolean with composable pause reasons, and adding disabled-by-default runtime tracing for A/B validation.

**Architecture:** Start from the exact public V9.9.2 Portable artifact and apply one deterministic, hash-gated V9.9.3 overlay. Keep the existing high-frequency C2 minimap thread, but change it from `behavior_engine.tick(...)` ownership to `SpotifyMainFarmOrchestrator.tick(..., owner="C2")`; the full-screen supervisor must not execute the same C2 farm stages. Use a small `spotify_c2_runtime_support.py` module for pause-reason composition and low-overhead buffered trace records; keep C1/B1/B3/Pirate/Bunny/Stand Still on their existing paths.

**Tech Stack:** Python 3.12, Tkinter, OpenCV, MSS, PyDirectInput, pytest, Nuitka one-file, GitHub Actions Windows runner.

**Spec:** `docs/superpowers/specs/2026-09-13-c2-runtime-parity-design.md`

## Global Constraints

- Exact public base is `v9.9.2`; do not mutate or overwrite existing V9.9.2 release assets.
- Public V9.9.2 Portable SHA-256 is `7359f223339bf857fcbe68c7df036d6857cfe7b81a49ce76d5a217001f8a10b4`.
- Current source hashes inside the V9.9.2 implementation are:
  - `app_payload/spotify_recovered_core.py` = `961ee533f03c01a9fd2b62f58900ad8af7b7a8aabcca3612d25b1f21adb42019`
  - `app_payload/maple_nghia_pro.py` = `85c05cfb2645fb756f5a644564972b59388c5d39e385f439b3065d369dc8142d`
  - `app_payload/spotify_behavior_engine.py` = `de137e5486518d183e26b83d360fa4a164e0fd136ce1deef003d6ad7b953fe97`
  - `app_payload/spotify_main_farm_orchestrator.py` = `63ca972e4b051905fdb862d64c8a8f29e73b28282a0c2711180680d1d535b2c6`
  - `app_payload/spotify_recovered_api.py` = `1ceb0d194d1edfcab1a8005ac7fdd04343a90ff6962dc77d2dc675aac06a4339`
  - `app_payload/spotify_timing_catalog.py` = `b1eab666bc1227fbb420695ffcdc5ea97dde6880a49cc15b42b88aa1633c1066`
  - `app_payload/spotify_focus_parity.py` = `987774bdca786302001a0145474761986a0e8f9539b7f277157b40bf5b6fb9d1`
  - `app_payload/maps.json` = `52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d`
- C2 alone may use the runtime-supported `20..50 ms` action-hold / `50..150 ms` pair-wait candidate.
- C2 outer window stays `0.200..0.500 s`; pre-combo delay stays `0.05 s`; PyDirectInput `PAUSE=0.10` is not reduced.
- C1/B1/B3, Pirate normal/1-Hit, Bunny, Stand Still, MiuMiu, All Cure, watchdog thresholds, focus worker cadence/cache, maps, updater, session exclusion, and CAPTCHA detect/pause/alert-only behavior must remain behaviorally unchanged except for replacing C2 pause ownership plumbing.
- Dynamic Combo remains definition-only/dormant.
- Trace is disabled by default and must not contain credentials/session data.
- Publication is forbidden in this plan. Produce a private preflight artifact only; do not create a GitHub Release and do not update `main/latest.json`.

---

## File Structure

Create these V9.9.3 release files in the repository:

```text
release_payload/v9.9.3-c2-runtime-parity/
  README.md
  apply_overlay.py
  spotify_c2_runtime_support.py
  tests/
    test_c2_runtime_support.py
    test_c2_runtime_combo.py
    test_c2_mainfarm_owner.py
    test_c2_protected_profiles.py

.github/workflows/
  preflight-v9.9.3-c2-runtime-parity.yml
```

The overlay modifies only these extracted app files:

```text
app_payload/spotify_recovered_core.py
app_payload/spotify_main_farm_orchestrator.py
app_payload/maple_nghia_pro.py
```

and adds:

```text
app_payload/spotify_c2_runtime_support.py
```

`spotify_behavior_engine.py`, `spotify_recovered_api.py`, `spotify_timing_catalog.py`, `spotify_focus_parity.py`, `maps.json`, Pirate modules/logic, MiuMiu, All Cure executor/market implementation, launcher files, and updater files remain hash-protected.

---

### Task 1: RED Tests for C2 Runtime Contracts

**Files:**
- Create: `release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_runtime_support.py`
- Create: `release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_runtime_combo.py`
- Create: `release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_mainfarm_owner.py`
- Create: `release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_protected_profiles.py`

**Interfaces:**
- Consumes: extracted public V9.9.2 app payload via `APP_PAYLOAD` environment variable.
- Produces: failing tests that define pause-reason, C2 microtiming, main-farm ownership, and protected-profile contracts.

- [ ] **Step 1: Write failing support tests**

Create `test_c2_runtime_support.py` with these exact behavioral assertions:

```python
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
```

- [ ] **Step 2: Write failing C2 combo tests**

Create `test_c2_runtime_combo.py` with a fake clock and deterministic random recorder so the test checks ranges rather than wall-clock timing:

```python
import os
import sys
from pathlib import Path

APP_PAYLOAD = Path(os.environ["APP_PAYLOAD"])
sys.path.insert(0, str(APP_PAYLOAD))

import spotify_recovered_core as core_module
from spotify_recovered_core import SpotifyRecoveredCore


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += float(seconds)


def make_core():
    core = SpotifyRecoveredCore.__new__(SpotifyRecoveredCore)
    core.host = object()
    core.current_move_key = None
    core.spotify_input_last_role = "IDLE"
    core.spotify_input_role = "IDLE"
    core.spotify_scheduler_last_action = ""
    core._focus_game = lambda cfg: True
    core.set_move = lambda key: setattr(core, "current_move_key", key)
    core._release_all_owned_inputs = lambda: None
    return core


def test_c2_combo_draws_only_20_50_action_and_50_150_wait(monkeypatch):
    core = make_core()
    clock = FakeClock()
    draws = []
    presses = []

    def fake_randint(lo, hi):
        draws.append(("randint", lo, hi))
        return lo

    def fake_uniform(lo, hi):
        draws.append(("uniform", lo, hi))
        return lo

    core._press_input_key = lambda key, hold_ms=None: presses.append((key, hold_ms)) or True
    monkeypatch.setattr(core_module.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(core_module.time, "sleep", clock.sleep)
    monkeypatch.setattr(core_module.random, "randint", fake_randint)
    monkeypatch.setattr(core_module.random, "uniform", fake_uniform)

    assert core._spotify_c2_tp_skill_hold_combo(
        {"tele_key": "X", "tele_enabled": True}, "RIGHT", "A", 0.20
    ) is True

    assert presses
    assert all(lo == 20 and hi == 50 for kind, lo, hi in draws if kind == "randint")
    assert all(lo == 0.05 and hi == 0.15 for kind, lo, hi in draws if kind == "uniform")
    assert presses[0][0] == "X"
    assert presses[1][0] == "A"


def test_c2_skill_only_keeps_same_runtime_timing_family(monkeypatch):
    core = make_core()
    clock = FakeClock()
    presses = []
    draws = []
    core._press_input_key = lambda key, hold_ms=None: presses.append((key, hold_ms)) or True
    monkeypatch.setattr(core_module.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(core_module.time, "sleep", clock.sleep)
    monkeypatch.setattr(core_module.random, "randint", lambda lo, hi: draws.append(("r", lo, hi)) or lo)
    monkeypatch.setattr(core_module.random, "uniform", lambda lo, hi: draws.append(("u", lo, hi)) or lo)

    assert core._spotify_c2_tp_skill_hold_combo(
        {"tele_key": "", "tele_enabled": False}, "RIGHT", "A", 0.20
    ) is True
    assert all(key == "A" for key, _ in presses)
    assert ("r", 20, 50) in draws
    assert ("u", 0.05, 0.15) in draws


def test_primary_skill_step_routes_only_c2_to_c2_runtime_helper():
    source = (APP_PAYLOAD / "spotify_recovered_core.py").read_text(encoding="utf-8")
    start = source.index("    def _spotify_primary_skill_step")
    end = source.index("    def _spotify_turn_action", start)
    body = source[start:end]
    assert 'current_map' in body
    assert '"C2"' in body
    assert "_spotify_c2_tp_skill_hold_combo" in body
    assert "_spotify_hold_combo_action" in body
```

- [ ] **Step 3: Write failing main-farm owner tests**

Create `test_c2_mainfarm_owner.py`:

```python
import os
import sys
from pathlib import Path

APP_PAYLOAD = Path(os.environ["APP_PAYLOAD"])
sys.path.insert(0, str(APP_PAYLOAD))

from spotify_main_farm_orchestrator import SpotifyMainFarmOrchestrator, CONTINUE


class RecordingHost:
    def __init__(self):
        self.calls = []

    def _stage(self, name, owner):
        self.calls.append((name, owner))
        return CONTINUE

    def _spotify_mainfarm_state_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("STATE", owner)

    def _spotify_mainfarm_sell_safe_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("SELL_SAFE", owner)

    def _spotify_mainfarm_pet_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("PET", owner)

    def _spotify_mainfarm_recovery_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("RECOVERY", owner)

    def _spotify_mainfarm_buff1_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("BUFF1", owner)

    def _spotify_mainfarm_buff2_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("BUFF2", owner)

    def _spotify_mainfarm_dispatch_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("DISPATCH", owner)


def test_c2_owner_runs_exact_recovered_stage_order():
    host = RecordingHost()
    SpotifyMainFarmOrchestrator(host).tick({}, (100.0, 170.0), 1.0, owner="C2")
    assert host.calls == [
        ("STATE", "C2"),
        ("SELL_SAFE", "C2"),
        ("PET", "C2"),
        ("RECOVERY", "C2"),
        ("BUFF1", "C2"),
        ("BUFF2", "C2"),
        ("DISPATCH", "C2"),
    ]


def test_source_has_single_c2_farm_owner_and_supervisor_skip():
    source = (APP_PAYLOAD / "maple_nghia_pro.py").read_text(encoding="utf-8")
    worker_start = source.index("    def _c2_fast_farm_worker")
    worker_end = source.index("    @staticmethod\n    def _spotify_profile_kind_from", worker_start)
    worker = source[worker_start:worker_end]
    assert 'spotify_main_farm_orchestrator.tick(cfg, map_pos' in worker
    assert 'owner="C2"' in worker
    assert "self.behavior_engine.tick(cfg, map_pos" not in worker

    bot_start = source.index("    def bot_loop")
    bot = source[bot_start:]
    assert "if c2_fast_owned:" in bot
    assert 'owner="SUPERVISOR"' in bot
```

- [ ] **Step 4: Write protected-profile source/hash tests**

Create `test_c2_protected_profiles.py`:

```python
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


def test_protected_files_remain_byte_identical():
    for name, expected in PROTECTED.items():
        assert sha(APP_PAYLOAD / name) == expected


def test_dynamic_combo_is_still_not_in_active_dispatch():
    behavior = (APP_PAYLOAD / "spotify_behavior_engine.py").read_text(encoding="utf-8")
    assert "perform_dynamic_combo" not in behavior


def test_pirate_paths_still_use_shared_helper_not_c2_helper():
    core = (APP_PAYLOAD / "spotify_recovered_core.py").read_text(encoding="utf-8")
    start = core.index("    def _spotify_pirate_normal_farm_step")
    end = core.index("    def _spotify_pirate_1hit_farm_step", start)
    pirate = core[start:end]
    assert "_spotify_hold_combo_action" in pirate
    assert "_spotify_c2_tp_skill_hold_combo" not in pirate
```

- [ ] **Step 5: Run RED tests on unmodified V9.9.2**

Run:

```powershell
$env:APP_PAYLOAD = (Resolve-Path '.\base\app_payload')
python -m pytest release_payload/v9.9.3-c2-runtime-parity/tests -q
```

Expected before implementation:

```text
FAIL: spotify_c2_runtime_support import missing
FAIL: primary C2 farm still routes through shared _spotify_hold_combo_action
FAIL: orchestrator.tick has no owner argument
FAIL: C2 worker still calls behavior_engine.tick directly
```

- [ ] **Step 6: Commit the RED tests**

```bash
git add release_payload/v9.9.3-c2-runtime-parity/tests
git commit -m "test: define V9.9.3 C2 runtime parity contracts"
```

---

### Task 2: Add Pause-Reason Gate and Buffered Runtime Trace

**Files:**
- Create: `release_payload/v9.9.3-c2-runtime-parity/spotify_c2_runtime_support.py`
- Modify through overlay: `app_payload/maple_nghia_pro.py`
- Test: `release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_runtime_support.py`

**Interfaces:**
- Produces: `C2PauseReasons.add/remove/clear/blocked/snapshot` and `C2RuntimeTraceBuffer.emit/snapshot/dump`.
- Host helpers produced in `maple_nghia_pro.py`: `_c2_pause_add`, `_c2_pause_remove`, `_c2_pause_blocked`, `_c2_trace_emit`, `_c2_trace_dump`.

- [ ] **Step 1: Add the support module**

Create `spotify_c2_runtime_support.py` with this implementation:

```python
from __future__ import annotations

import json
import threading
import time
from pathlib import Path


class C2PauseReasons:
    def __init__(self):
        self._lock = threading.RLock()
        self._reasons = set()

    def add(self, reason: str) -> None:
        reason = str(reason or "").strip().lower()
        if not reason:
            return
        with self._lock:
            self._reasons.add(reason)

    def remove(self, reason: str) -> None:
        reason = str(reason or "").strip().lower()
        with self._lock:
            self._reasons.discard(reason)

    def clear(self) -> None:
        with self._lock:
            self._reasons.clear()

    def blocked(self) -> bool:
        with self._lock:
            return bool(self._reasons)

    def snapshot(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._reasons))


class C2RuntimeTraceBuffer:
    def __init__(self, enabled=False, max_records=100000):
        self.enabled = bool(enabled)
        self.max_records = max(1, int(max_records))
        self._lock = threading.RLock()
        self._records = []

    def emit(self, event: str, **fields) -> None:
        if not self.enabled:
            return
        row = {"t_ns": time.perf_counter_ns(), "event": str(event)}
        row.update(fields)
        with self._lock:
            if len(self._records) >= self.max_records:
                self._records.pop(0)
            self._records.append(row)

    def snapshot(self):
        with self._lock:
            return list(self._records)

    def dump(self, path) -> None:
        if not self.enabled:
            return
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        rows = self.snapshot()
        target.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
```

- [ ] **Step 2: Patch host initialization and helper methods**

Overlay these imports into `maple_nghia_pro.py`:

```python
from spotify_c2_runtime_support import C2PauseReasons, C2RuntimeTraceBuffer
from client_paths import default_or_user_file, resolve_mutable_file
```

Replace the `c2_fast_supervisor_pause` initialization with:

```python
self.c2_pause_reasons = C2PauseReasons()
self.c2_runtime_trace = C2RuntimeTraceBuffer(
    enabled=str(os.environ.get("NGHIA_C2_RUNTIME_TRACE", "")).strip() == "1"
)
self.c2_runtime_trace_path = resolve_mutable_file(
    "c2_runtime_trace.jsonl", Path(__file__).resolve().parent
)
```

Add `import os` at the top of `maple_nghia_pro.py`.

Add these host helpers:

```python
def _c2_pause_add(self, reason):
    self.c2_pause_reasons.add(reason)
    self._c2_trace_emit("pause_add", reason=str(reason))
    self.behavior_engine.release_inputs()


def _c2_pause_remove(self, reason):
    self.c2_pause_reasons.remove(reason)
    self._c2_trace_emit("pause_remove", reason=str(reason))


def _c2_pause_blocked(self):
    return self.c2_pause_reasons.blocked()


def _c2_trace_emit(self, event, **fields):
    self.c2_runtime_trace.emit(event, **fields)


def _c2_trace_dump(self):
    try:
        self.c2_runtime_trace.dump(self.c2_runtime_trace_path)
    except Exception as exc:
        self._log(f"[C2 Trace] dump failed: {exc}")
```

- [ ] **Step 3: Make start/stop reset and persist trace safely**

At C2 worker start:

```python
self.c2_pause_reasons.clear()
```

At `stop_bot()` before generation invalidation:

```python
self._c2_pause_add("stop")
```

At the end of `stop_bot()`:

```python
self._c2_trace_dump()
```

- [ ] **Step 4: Run support tests GREEN**

Run:

```powershell
$env:APP_PAYLOAD = (Resolve-Path '.\patched\app_payload')
python -m pytest release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_runtime_support.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit support module and overlay changes**

```bash
git add release_payload/v9.9.3-c2-runtime-parity/spotify_c2_runtime_support.py \
        release_payload/v9.9.3-c2-runtime-parity/apply_overlay.py
git commit -m "feat: add composable C2 pause and runtime trace support"
```

---

### Task 3: Wire the C2-Only Runtime Combo Candidate

**Files:**
- Modify through overlay: `app_payload/spotify_recovered_core.py`
- Test: `release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_runtime_combo.py`

**Interfaces:**
- Consumes: existing `SPOTIFY_R54_COMBO_SPAM_ACTION_MS = (20, 50)` and `SPOTIFY_R54_COMBO_SPAM_WAIT_S = (0.05, 0.15)`.
- Produces: C2-only `_spotify_c2_tp_skill_hold_combo(...)` with the same timing family for TP+Skill and Skill-only, and C2 routing from `_spotify_primary_skill_step(...)`.

- [ ] **Step 1: Replace the C2 helper with monotonic timing and no shared-helper fallback**

Use this body for `_spotify_c2_tp_skill_hold_combo`:

```python
def _spotify_c2_tp_skill_hold_combo(self, cfg, direction_key, skill_key, hold_time):
    flash_key = str(cfg.get("tele_key") or "").strip()
    skill_key = str(skill_key or "").strip()
    if not direction_key or not skill_key or not self._focus_game(cfg):
        return False

    use_flash = bool(flash_key and cfg.get("tele_enabled", True))
    end_time = time.monotonic() + max(0.02, float(hold_time))
    self.set_move(direction_key)
    did = False
    trace = getattr(self.host, "_c2_trace_emit", None)
    if trace:
        trace("combo_start", hold_time_s=float(hold_time), direction=str(direction_key))
    try:
        while time.monotonic() < end_time:
            if use_flash:
                hold_ms = random.randint(*SPOTIFY_R54_COMBO_SPAM_ACTION_MS)
                if trace:
                    trace("teleport_down", key=flash_key, hold_ms=hold_ms)
                did = bool(self._press_input_key(flash_key, hold_ms=hold_ms)) or did
                if trace:
                    trace("teleport_up", key=flash_key)

            hold_ms = random.randint(*SPOTIFY_R54_COMBO_SPAM_ACTION_MS)
            if trace:
                trace("skill_down", key=skill_key, hold_ms=hold_ms)
            did = bool(self._press_input_key(skill_key, hold_ms=hold_ms)) or did
            if trace:
                trace("skill_up", key=skill_key)

            wait_s = random.uniform(*SPOTIFY_R54_COMBO_SPAM_WAIT_S)
            if trace:
                trace("pair_wait_start", wait_s=wait_s)
            time.sleep(wait_s)
            if trace:
                trace("pair_wait_end", wait_s=wait_s)
    except Exception:
        self._release_all_owned_inputs()
        raise
    finally:
        if trace:
            trace("combo_end", did=bool(did))

    if did:
        self.spotify_input_last_role = "C2_TP_SKILL"
        self.spotify_scheduler_last_action = "C2_TP_SKILL"
    return did
```

- [ ] **Step 2: Route only C2 through the C2 helper**

In `_spotify_primary_skill_step`, keep the recovered `0.05 s` pre-combo sleep and `200..500 ms` outer window, then replace the single shared-helper call with:

```python
current_map = str(cfg.get("current_map", "")).strip().upper()
if current_map == "C2" and bool(cfg.get("spotify_runtime_parity_mode", True)):
    ok = self._spotify_c2_tp_skill_hold_combo(
        cfg,
        direction_key if direction_key else None,
        skill_key,
        combo_ms / 1000.0,
    )
else:
    ok = self._spotify_hold_combo_action(
        cfg,
        direction_key if direction_key else None,
        flash_key or None,
        skill_key,
        combo_ms / 1000.0,
    )
```

Do not modify Pirate calls to `_spotify_hold_combo_action`.

- [ ] **Step 3: Run C2 combo tests GREEN**

Run:

```powershell
$env:APP_PAYLOAD = (Resolve-Path '.\patched\app_payload')
python -m pytest release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_runtime_combo.py -q
```

Expected: all tests pass.

- [ ] **Step 4: Run protected profile tests**

Run:

```powershell
python -m pytest release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_protected_profiles.py -q
```

Expected: all tests pass, proving behavior/API/timing catalog/focus/maps hashes remain unchanged and Pirate still uses the shared helper.

- [ ] **Step 5: Commit C2-only microtiming routing**

```bash
git add release_payload/v9.9.3-c2-runtime-parity/apply_overlay.py \
        release_payload/v9.9.3-c2-runtime-parity/tests
git commit -m "feat: route C2 through runtime-supported combo timing"
```

---

### Task 4: Make the C2 Minimap Worker the Sole Main-Farm Owner

**Files:**
- Modify through overlay: `app_payload/spotify_main_farm_orchestrator.py`
- Modify through overlay: `app_payload/maple_nghia_pro.py`
- Test: `release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_mainfarm_owner.py`

**Interfaces:**
- Produces: `SpotifyMainFarmOrchestrator.tick(cfg, map_pos, now, owner="SUPERVISOR")`.
- C2 worker calls `owner="C2"`; supervisor calls `owner="SUPERVISOR"` only when it owns the profile.

- [ ] **Step 1: Extend orchestrator owner propagation**

Replace `SpotifyMainFarmOrchestrator.tick` with:

```python
def tick(self, cfg, map_pos, now, owner="SUPERVISOR"):
    stages = (
        self.host._spotify_mainfarm_state_stage,
        self.host._spotify_mainfarm_sell_safe_stage,
        self.host._spotify_mainfarm_pet_stage,
        self.host._spotify_mainfarm_recovery_stage,
        self.host._spotify_mainfarm_buff1_stage,
        self.host._spotify_mainfarm_buff2_stage,
        self.host._spotify_mainfarm_dispatch_stage,
    )
    for stage in stages:
        if stage(cfg, map_pos, now, owner=owner) == STOP_TICK:
            return STOP_TICK
    return CONTINUE
```

- [ ] **Step 2: Add `owner` keyword to all seven host stage methods**

Change the signatures to:

```python
def _spotify_mainfarm_state_stage(self, cfg, map_pos, now, owner="SUPERVISOR"):
def _spotify_mainfarm_sell_safe_stage(self, cfg, map_pos, now, owner="SUPERVISOR"):
def _spotify_mainfarm_pet_stage(self, cfg, map_pos, now, owner="SUPERVISOR"):
def _spotify_mainfarm_recovery_stage(self, cfg, map_pos, now, owner="SUPERVISOR"):
def _spotify_mainfarm_buff1_stage(self, cfg, map_pos, now, owner="SUPERVISOR"):
def _spotify_mainfarm_buff2_stage(self, cfg, map_pos, now, owner="SUPERVISOR"):
def _spotify_mainfarm_dispatch_stage(self, cfg, map_pos, now, owner="SUPERVISOR"):
```

Emit trace markers at stage entry when `owner == "C2"`:

```python
if owner == "C2":
    self._c2_trace_emit("stage", name="STATE")
```

Use names exactly: `STATE`, `SELL_SAFE`, `PET`, `RECOVERY`, `BUFF1`, `BUFF2`, `DISPATCH`.

- [ ] **Step 3: Remove C2 skip branches from Pet/Recovery/Buff/Dispatch**

Delete these C2-specific early returns:

```python
if self._c2_fast_worker_owns(cfg):
    return CONTINUE
```

and delete the C2 dispatch skip:

```python
if c2_fast_owned:
    self.c2_fast_supervisor_pause = False
    return STOP_TICK
```

Keep the input lock and existing stage internals unchanged.

- [ ] **Step 4: Change the C2 worker from behavior-engine owner to main-farm owner**

In `_c2_fast_farm_worker`, replace:

```python
self.behavior_engine.tick(cfg, map_pos, time.monotonic())
```

with:

```python
now = time.monotonic()
self._c2_trace_emit("tick_start")
self.spotify_main_farm_orchestrator.tick(
    cfg, map_pos, now, owner="C2"
)
self._c2_trace_emit("tick_end")
```

Keep the minimap-only capture path and the tiny `time.sleep(0.001)` yield unchanged.

- [ ] **Step 5: Make the supervisor skip C2 farm orchestration**

In `bot_loop`, replace the unconditional call:

```python
self.spotify_main_farm_orchestrator.tick(cfg, map_pos, now)
```

with:

```python
if not c2_fast_owned:
    self.spotify_main_farm_orchestrator.tick(
        cfg, map_pos, now, owner="SUPERVISOR"
    )
```

The supervisor continues capture, preview, alerts, status, and other non-farm work.

- [ ] **Step 6: Run owner tests GREEN**

Run:

```powershell
$env:APP_PAYLOAD = (Resolve-Path '.\patched\app_payload')
python -m pytest release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_mainfarm_owner.py -q
```

Expected: both tests pass.

- [ ] **Step 7: Commit sole-owner main-farm changes**

```bash
git add release_payload/v9.9.3-c2-runtime-parity/apply_overlay.py \
        release_payload/v9.9.3-c2-runtime-parity/tests
git commit -m "feat: make C2 worker the sole main-farm owner"
```

---

### Task 5: Replace Boolean Pause Ownership at Every C2 Input Takeover

**Files:**
- Modify through overlay: `app_payload/maple_nghia_pro.py`
- Test: `release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_runtime_support.py`
- Test: `release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_mainfarm_owner.py`

**Interfaces:**
- Consumes: `C2PauseReasons` from Task 2.
- Produces: reason-specific pause add/remove for `sell`, `captcha`, `disconnect`, `revive`, `all_cure`, `stop`.

- [ ] **Step 1: Gate the C2 worker by pause reasons**

Replace the worker condition that checks `c2_fast_supervisor_pause` with:

```python
if (self._c2_pause_blocked() or self.sell_lock.locked()
        or bool(cfg.get("preview_only", False))):
    self.behavior_engine.release_inputs()
    time.sleep(0.01)
    continue
```

- [ ] **Step 2: Convert seller ownership to `sell` reason**

In `_sell_sequence_worker`, wrap the seller body as:

```python
self._c2_pause_add("sell")
try:
    with self.sell_lock:
        self.behavior_engine.release_inputs()
        # existing seller body remains unchanged here
        ...
finally:
    self._c2_pause_remove("sell")
```

The implementation must move the existing seller body unchanged into the `try` block; it must not duplicate it. `spotify_sell_inflight`, watchdog completion notification, retry event behavior, and MiuMiu calls remain unchanged.

- [ ] **Step 3: Convert All Cure ownership to `all_cure` reason**

Wrap `_spotify_market_run_action`:

```python
def _spotify_market_run_action(self, action_name, actions, cfg):
    self._c2_pause_add("all_cure")
    try:
        self.behavior_engine.release_inputs()
        worker = self.spotify_all_cure_market
        status = worker.gateway_status()
        if not worker.workflow_ready() or not status.ready:
            self._log(f"[Spotify All Cure] {action_name}: gateway/workflow BLOCKED; action skipped.")
            return False
        executor = SpotifyAllCureExecutor(self, worker.gateway)
        return bool(executor.run(actions, cfg))
    finally:
        self._c2_pause_remove("all_cure")
```

- [ ] **Step 4: Convert watchdog pause handling**

Change `_spotify_watchdog_request_pause` to:

```python
def _spotify_watchdog_request_pause(self, reason, cfg):
    normalized = {
        "dead": "revive",
        "disconnect": "disconnect",
        "captcha": "captcha",
    }.get(str(reason).strip().lower(), str(reason).strip().lower())
    self._c2_pause_add(normalized)
    self._log(f"[Spotify Watchdog] pause: {reason}")
    return True
```

Change disconnect clear path:

```python
if not result.matched:
    self.spotify_disconnect_latched = False
    self._c2_pause_remove("disconnect")
    return False
```

Change `_spotify_watchdog_emit` unmatched handling so CAPTCHA clears independently:

```python
if not result.matched:
    if result.kind == "captcha":
        self._c2_pause_remove("captcha")
    return
```

Wrap revive click ownership so only the revive action owns the reason:

```python
self._spotify_watchdog_request_pause("dead", cfg)
try:
    # existing evidenced revive click body
    ...
finally:
    self._c2_pause_remove("revive")
```

If `pause_on_alert` stops the tool, `stop_bot` / generation invalidation remains the terminal safety owner.

- [ ] **Step 5: Remove all remaining runtime reads/writes of `c2_fast_supervisor_pause`**

Run:

```bash
rg -n "c2_fast_supervisor_pause" patched/app_payload/maple_nghia_pro.py
```

Expected: no matches.

Do not remove C2 fast worker state fields unrelated to pause ownership (`c2_fast_thread`, generation, last position, last seen, capture failures).

- [ ] **Step 6: Add a source-level pause ownership regression**

Append to `test_c2_runtime_support.py`:

```python
def test_legacy_c2_pause_boolean_is_removed():
    source = (APP_PAYLOAD / "maple_nghia_pro.py").read_text(encoding="utf-8")
    assert "c2_fast_supervisor_pause" not in source
    for reason in ("sell", "captcha", "disconnect", "revive", "all_cure", "stop"):
        assert f'"{reason}"' in source
```

- [ ] **Step 7: Run pause/owner tests GREEN**

```powershell
python -m pytest \
  release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_runtime_support.py \
  release_payload/v9.9.3-c2-runtime-parity/tests/test_c2_mainfarm_owner.py -q
```

Expected: all pass.

- [ ] **Step 8: Commit pause ownership integration**

```bash
git add release_payload/v9.9.3-c2-runtime-parity/apply_overlay.py \
        release_payload/v9.9.3-c2-runtime-parity/tests
git commit -m "fix: compose C2 pause reasons across input owners"
```

---

### Task 6: Deterministic Overlay, Hash Gates, and Private Package Metadata

**Files:**
- Create/finish: `release_payload/v9.9.3-c2-runtime-parity/apply_overlay.py`
- Create: `release_payload/v9.9.3-c2-runtime-parity/README.md`

**Interfaces:**
- Consumes: exact public V9.9.2 extracted root.
- Produces: deterministic patched app payload with only three modified source files plus one new support module.

- [ ] **Step 1: Make `apply_overlay.py` refuse the wrong base**

At minimum gate these base hashes before any write:

```python
BASE_HASHES = {
    "app_payload/spotify_recovered_core.py": "961ee533f03c01a9fd2b62f58900ad8af7b7a8aabcca3612d25b1f21adb42019",
    "app_payload/maple_nghia_pro.py": "85c05cfb2645fb756f5a644564972b59388c5d39e385f439b3065d369dc8142d",
    "app_payload/spotify_main_farm_orchestrator.py": "63ca972e4b051905fdb862d64c8a8f29e73b28282a0c2711180680d1d535b2c6",
}
```

Also verify every protected hash listed in Global Constraints before writes.

- [ ] **Step 2: Use exact-count replacements**

Use a helper that fails unless each intended source fragment occurs exactly once:

```python
def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)
```

Normalize newly written Python files to LF using `Path.write_text(..., newline="\n")` so Git-for-Windows checkout does not change packaged hashes.

- [ ] **Step 3: Copy support module into `app_payload` and verify final diff set**

After patching, compute the app `.py/.json` hash map before/after. The only allowed changed/new source paths are:

```text
app_payload/spotify_recovered_core.py
app_payload/spotify_main_farm_orchestrator.py
app_payload/maple_nghia_pro.py
app_payload/spotify_c2_runtime_support.py
```

Any other source/evidence/config change aborts the overlay.

- [ ] **Step 4: Keep private V9.9.3 metadata separate from public stable**

For the private artifact set:

```json
{"version":"9.9.3","variant":"C2RuntimeParity"}
```

Do not modify repository `main/latest.json` and do not create a public release manifest.

- [ ] **Step 5: Write README with evidence boundary**

`README.md` must state:

```text
V9.9.3 C2 Runtime Parity is a PRIVATE candidate.
20–50ms action hold / 50–150ms pair wait is runtime-supported by binary adjacency + Spotify video distribution, not claimed as byte-for-byte Python source recovery.
C2 alone uses the candidate timing.
C1/B1/B3/Pirate/Bunny/Stand Still remain on V9.9.2 behavior.
Runtime parity requires same-machine A/B validation after preflight.
No public release/latest.json update is performed by this workflow.
```

- [ ] **Step 6: Run all V9.9.3 tests on the fully patched payload**

```powershell
$env:APP_PAYLOAD = (Resolve-Path '.\patched\app_payload')
python -m pytest release_payload/v9.9.3-c2-runtime-parity/tests -q
```

Expected: all pass.

- [ ] **Step 7: Commit deterministic overlay**

```bash
git add release_payload/v9.9.3-c2-runtime-parity
git commit -m "build: add deterministic V9.9.3 C2 runtime parity overlay"
```

---

### Task 7: Full Regression, Nuitka Build, and Windows Private Preflight

**Files:**
- Create: `.github/workflows/preflight-v9.9.3-c2-runtime-parity.yml`

**Interfaces:**
- Consumes: public V9.9.2 Portable, V9.9.3 overlay, all historical regression suites.
- Produces: private artifact `v9.9.3-c2-runtime-parity-preflight` containing Portable, Update, `preflight_hashes.txt`, and `preflight_report.json`.

- [ ] **Step 1: Create Windows workflow with exact public base gate**

The workflow must:

```powershell
New-Item -ItemType Directory -Force base, patched, dist | Out-Null
Invoke-WebRequest `
  -Uri "https://github.com/bachlangcomic-creator/maplenghia/releases/download/v9.9.2/NghiaClient_V9.9.2_Portable.zip" `
  -OutFile base.zip
$got = (Get-FileHash base.zip -Algorithm SHA256).Hash.ToLower()
if ($got -ne "7359f223339bf857fcbe68c7df036d6857cfe7b81a49ce76d5a217001f8a10b4") {
    throw "public V9.9.2 base hash mismatch: $got"
}
Expand-Archive base.zip base
Copy-Item base\* patched -Recurse -Force
python release_payload/v9.9.3-c2-runtime-parity/apply_overlay.py patched
```

- [ ] **Step 2: Run complete regression matrix**

Reuse the exact historical test commands from the V9.9.2/private PirateParity+API preflight, then append:

```powershell
$env:APP_PAYLOAD = (Resolve-Path 'patched\app_payload')
python -m pytest release_payload/v9.9.3-c2-runtime-parity/tests -q
```

The workflow must fail on any test failure/error.

- [ ] **Step 3: Compile/import final payload before binary build**

Run:

```powershell
python -m compileall -q patched\app_payload
python -c "import sys; sys.path.insert(0, r'patched\app_payload'); import spotify_c2_runtime_support, spotify_recovered_core, spotify_main_farm_orchestrator, spotify_behavior_engine"
```

Expected: exit code 0.

- [ ] **Step 4: Build with the same Nuitka one-file path as V9.9.2**

Use the current V9.9.2 Nuitka command and explicitly include the new module:

```text
--include-module=spotify_c2_runtime_support
```

Do not switch to PyInstaller.

- [ ] **Step 5: Reject PyInstaller carry-over**

Check the rebuilt EXE bytes and fail if either marker appears:

```text
_MEIPASS
pyiboot01_bootstrap
```

- [ ] **Step 6: Run the real Windows launcher smoke**

Use the same launcher/default-launch smoke command that passed V9.9.2. Require the process to start through `NghiaLauncher`/default launch path and exit the smoke harness successfully.

- [ ] **Step 7: Package private Portable and Update artifacts**

Names:

```text
NghiaClient_V9.9.3_C2RuntimeParity_Portable.zip
NghiaEdition_Update_v9.9.3_C2RuntimeParity.zip
preflight_hashes.txt
preflight_report.json
```

`preflight_report.json` must include at least:

```json
{
  "version": "9.9.3",
  "variant": "C2RuntimeParity",
  "failures": 0,
  "errors": 0,
  "base_public_v9.9.2_sha256": "7359f223339bf857fcbe68c7df036d6857cfe7b81a49ce76d5a217001f8a10b4",
  "c2_action_hold_ms": [20, 50],
  "c2_pair_wait_s": [0.05, 0.15],
  "c2_outer_window_s": [0.2, 0.5],
  "c2_mainfarm_owner": "C2",
  "dynamic_combo_active": false,
  "public_publish_performed": false
}
```

Fill `tests`, `portable_sha256`, `update_sha256`, and patched-source hashes from the actual run.

- [ ] **Step 8: Upload artifact and hard-block publication**

Upload with:

```yaml
name: v9.9.3-c2-runtime-parity-preflight
```

End the workflow with an explicit assertion that no `latest.json` is generated/modified and no `gh release create` command exists in the workflow.

- [ ] **Step 9: Commit workflow**

```bash
git add .github/workflows/preflight-v9.9.3-c2-runtime-parity.yml
git commit -m "ci: add V9.9.3 C2 runtime parity private preflight"
```

---

### Task 8: Verification Before Completion and Runtime Handoff

**Files:**
- Read: GitHub Actions run result and uploaded preflight report.
- No source modifications unless verification exposes a defect.

**Interfaces:**
- Consumes: completed Windows preflight run.
- Produces: verified private artifact and an A/B runtime-test handoff; no parity claim before A/B evidence.

- [ ] **Step 1: Verify every workflow step is green**

Required successful stages:

```text
exact V9.9.2 base download/hash
V9.9.3 overlay
approved-only source diff
full regression + V9.9.3 tests
compile/import
Nuitka build
PyInstaller rejection
Windows launcher smoke
package/hash verification
artifact upload
public publishing locked
```

- [ ] **Step 2: Download the uploaded artifact and independently verify ZIP integrity/hashes**

Run `ZipFile.testzip()` on outer, Portable, and Update archives; recompute SHA-256 and compare with `preflight_report.json`.

- [ ] **Step 3: Verify protected sources again inside the final Portable**

Require the protected hashes from `test_c2_protected_profiles.py` to match exactly inside the packaged artifact.

- [ ] **Step 4: Verify C2 implementation markers in packaged source**

Check final packaged source contains:

```text
_spotify_c2_tp_skill_hold_combo
SPOTIFY_R54_COMBO_SPAM_ACTION_MS
SPOTIFY_R54_COMBO_SPAM_WAIT_S
owner="C2"
C2PauseReasons
C2RuntimeTraceBuffer
```

and contains no `c2_fast_supervisor_pause` reference.

- [ ] **Step 5: Report private-build status without overclaiming runtime parity**

The completion report must say:

```text
Static/CI parity candidate complete.
Runtime parity not yet claimed.
Next validation is same-machine Spotify vs V9.9.3 C2 trace/video using equivalent config.
Target reference remains roughly median 0.633 s, mean 0.637 s, p90 0.743 s.
```

Do not publish V9.9.3 in this task.
