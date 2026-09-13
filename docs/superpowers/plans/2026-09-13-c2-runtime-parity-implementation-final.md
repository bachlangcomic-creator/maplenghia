# Nghia V9.9.3 C2 Runtime Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a private V9.9.3 C2 candidate that is closer to Spotify at runtime by using the recovered 20–50 ms / 50–150 ms C2 timing candidate and a single C2 main-farm owner.

**Architecture:** Apply a deterministic overlay to exact public V9.9.2. C2 keeps the minimap-only worker, but that worker calls `SpotifyMainFarmOrchestrator.tick(..., owner="C2")`; the full-screen supervisor skips C2 farm stages. C1/B1/B3/Pirate/Bunny/Stand remain on V9.9.2 behavior.

**Tech Stack:** Python 3.12, pytest, PyDirectInput, OpenCV/MSS, Nuitka, Windows GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-13-c2-runtime-parity-design.md`

## Global Constraints

- Public V9.9.2 Portable SHA-256: `7359f223339bf857fcbe68c7df036d6857cfe7b81a49ce76d5a217001f8a10b4`.
- Base hashes: core `961ee533f03c01a9fd2b62f58900ad8af7b7a8aabcca3612d25b1f21adb42019`; UI `85c05cfb2645fb756f5a644564972b59388c5d39e385f439b3065d369dc8142d`; orchestrator `63ca972e4b051905fdb862d64c8a8f29e73b28282a0c2711180680d1d535b2c6`.
- Protected hashes must remain exact: behavior engine `de137e5486518d183e26b83d360fa4a164e0fd136ce1deef003d6ad7b953fe97`; recovered API `1ceb0d194d1edfcab1a8005ac7fdd04343a90ff6962dc77d2dc675aac06a4339`; timing catalog `b1eab666bc1227fbb420695ffcdc5ea97dde6880a49cc15b42b88aa1633c1066`; focus `987774bdca786302001a0145474761986a0e8f9539b7f277157b40bf5b6fb9d1`; maps `52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d`.
- C2 timing only: action hold `20..50 ms`, pair wait `0.05..0.15 s`, pre-combo `0.05 s`, outer window `0.2..0.5 s`, PyDirectInput `PAUSE=0.10` unchanged.
- Dynamic Combo remains dormant. No public release and no `latest.json` update.

---

### Task 1: RED Tests

**Files:** create four tests under `release_payload/v9.9.3-c2-runtime-parity/tests/`.

- [ ] Add `test_c2_runtime_support.py`: import `C2PauseReasons`; add `sell` and `captcha`; remove `sell`; assert still blocked; remove `captcha`; assert unblocked. Also assert disabled trace records nothing and enabled trace writes `t_ns` plus event.
- [ ] Add `test_c2_runtime_combo.py`: construct `SpotifyRecoveredCore.__new__`, fake `_focus_game`, `set_move`, `_press_input_key`, monkeypatch `time.monotonic/time.sleep/random.randint/random.uniform`, call `_spotify_c2_tp_skill_hold_combo`, and assert all `randint` draws are `(20,50)`, all `uniform` draws are `(0.05,0.15)`, TP precedes Skill, and Skill-only uses the same timing family.
- [ ] In the same combo test, slice `_spotify_primary_skill_step` source and assert C2 routes to `_spotify_c2_tp_skill_hold_combo` while the non-C2 branch still calls `_spotify_hold_combo_action`.
- [ ] Add `test_c2_mainfarm_owner.py`: fake seven stage methods and assert orchestrator order is exactly `STATE, SELL_SAFE, PET, RECOVERY, BUFF1, BUFF2, DISPATCH` with owner `C2`.
- [ ] Add `test_c2_protected_profiles.py`: assert protected hashes above, assert `perform_dynamic_combo` is absent from active behavior dispatch, and assert Pirate normal uses `_spotify_hold_combo_action` and not the C2 helper.
- [ ] Run on unmodified V9.9.2 and record expected RED failures: support module absent, orchestrator owner arg absent, C2 primary path not wired, C2 worker still calls `behavior_engine.tick`.
- [ ] Commit: `test: define V9.9.3 C2 runtime parity contracts`.

---

### Task 2: Pause Gate and Trace Support

**Files:** create `release_payload/v9.9.3-c2-runtime-parity/spotify_c2_runtime_support.py`; patch `maple_nghia_pro.py` through overlay.

- [ ] Implement `C2PauseReasons` with `RLock`, `add`, `remove`, `clear`, `blocked`, `snapshot`; `snapshot` returns sorted tuple.
- [ ] Implement `C2RuntimeTraceBuffer` with disabled-by-default `enabled`, `perf_counter_ns()` timestamps, bounded in-memory records, `snapshot`, and JSONL `dump(path)`.
- [ ] Patch UI imports to add `os`, `C2PauseReasons`, `C2RuntimeTraceBuffer`, and `resolve_mutable_file`.
- [ ] Replace `c2_fast_supervisor_pause` initialization with `self.c2_pause_reasons`, `self.c2_runtime_trace`, and mutable path `c2_runtime_trace.jsonl`; enable trace only when `NGHIA_C2_RUNTIME_TRACE=1`.
- [ ] Add `_c2_pause_add`, `_c2_pause_remove`, `_c2_pause_blocked`, `_c2_trace_emit`, `_c2_trace_dump`. `_c2_pause_add` must release behavior inputs after adding a reason.
- [ ] `_start_c2_fast_worker` clears reasons; `stop_bot` adds `stop`, invalidates generation, then dumps trace.
- [ ] Run support tests GREEN.
- [ ] Commit: `feat: add composable C2 pause and trace support`.

---

### Task 3: C2-Only Runtime Timing

**Files:** patch `spotify_recovered_core.py` through overlay.

- [ ] Replace `_spotify_c2_tp_skill_hold_combo` so it uses `time.monotonic()`, keeps movement held, uses `random.randint(*SPOTIFY_R54_COMBO_SPAM_ACTION_MS)` for TP and Skill, then `random.uniform(*SPOTIFY_R54_COMBO_SPAM_WAIT_S)` after the pair. If TP is disabled/missing, press Skill only with the same 20–50 / 50–150 family. On exception call `_release_all_owned_inputs()` and re-raise. Emit trace events `combo_start`, `teleport_down`, `teleport_up`, `skill_down`, `skill_up`, `pair_wait_start`, `pair_wait_end`, `combo_end` when host trace exists.
- [ ] In `_spotify_primary_skill_step`, preserve `SPOTIFY_SIMPLE_PRE_COMBO_SLEEP` and `SPOTIFY_SIMPLE_HOLD_COMBO_MS`; if current map is `C2` and runtime parity mode is enabled, call `_spotify_c2_tp_skill_hold_combo`; otherwise call existing `_spotify_hold_combo_action` exactly as V9.9.2.
- [ ] Run combo tests and protected-profile tests GREEN.
- [ ] Commit: `feat: route C2 through runtime-supported combo timing`.

---

### Task 4: Single C2 Main-Farm Owner

**Files:** patch `spotify_main_farm_orchestrator.py` and `maple_nghia_pro.py` through overlay.

- [ ] Change orchestrator signature to `tick(self, cfg, map_pos, now, owner="SUPERVISOR")` and invoke every stage with `owner=owner`.
- [ ] Add `owner="SUPERVISOR"` to all seven stage signatures. When owner is C2, emit stage trace using exact names `STATE`, `SELL_SAFE`, `PET`, `RECOVERY`, `BUFF1`, `BUFF2`, `DISPATCH`.
- [ ] Remove the C2 early-return skips from Pet, Recovery, Buff, and Dispatch. Keep existing input locks and stage internals.
- [ ] In `_c2_fast_farm_worker`, replace `behavior_engine.tick(...)` with `spotify_main_farm_orchestrator.tick(cfg, map_pos, now, owner="C2")`, bracketed by `tick_start/tick_end` trace events. Keep minimap-only capture and 1 ms yield.
- [ ] In `bot_loop`, if `_c2_fast_worker_owns(cfg)` is true, do not call the supervisor orchestrator; otherwise call it with `owner="SUPERVISOR"`.
- [ ] Run owner test GREEN.
- [ ] Commit: `feat: make C2 worker the sole main-farm owner`.

---

### Task 5: Replace Legacy Pause Boolean Everywhere

**Files:** patch `maple_nghia_pro.py` through overlay.

- [ ] C2 worker blocking condition becomes `self._c2_pause_blocked() or self.sell_lock.locked() or preview_only`.
- [ ] `_sell_sequence_worker`: call `_c2_pause_add("sell")` before entering seller ownership and `_c2_pause_remove("sell")` in `finally`; preserve the existing MiuMiu run call, error retry event, `spotify_sell_inflight`, `last_sell_time`, `last_timer_sell`, watchdog completion notification, and logs byte-for-byte inside the wrapper.
- [ ] `_spotify_market_run_action`: add `all_cure` before executor work and remove it in `finally`; preserve readiness checks and executor call.
- [ ] `_spotify_watchdog_request_pause`: normalize `dead -> revive`, `disconnect -> disconnect`, `captcha -> captcha`, then add the reason and release inputs.
- [ ] `_spotify_watchdog_request_revive`: wrap the existing evidenced center click in `try/finally` and remove `revive` in `finally`; preserve moveTo `0.10`, mouseDown, sleep `0.05`, mouseUp, dead-center clear, error mouseUp, and logs.
- [ ] `_spotify_disconnect_reaction`: when result no longer matches, clear latch and remove `disconnect`.
- [ ] `_spotify_watchdog_emit`: when a CAPTCHA result no longer matches, remove `captcha` before returning.
- [ ] Remove every read/write of `c2_fast_supervisor_pause`; `rg -n "c2_fast_supervisor_pause" patched/app_payload/maple_nghia_pro.py` must return no matches.
- [ ] Add regression asserting all six reason strings `sell, captcha, disconnect, revive, all_cure, stop` are present and legacy boolean is absent.
- [ ] Run support and owner tests GREEN.
- [ ] Commit: `fix: compose C2 pause reasons across input owners`.

---

### Task 6: Deterministic Overlay and Hash Gates

**Files:** create/finish `apply_overlay.py` and `README.md`.

- [ ] Before writes, gate the three base hashes and all five protected hashes from Global Constraints.
- [ ] Use a `replace_once` helper that aborts unless each source fragment occurs exactly once.
- [ ] Normalize overlay-written Python files to LF.
- [ ] Copy `spotify_c2_runtime_support.py` into `app_payload`.
- [ ] Compare app `.py/.json` hashes before/after. Allowed changed/new paths are exactly `spotify_recovered_core.py`, `spotify_main_farm_orchestrator.py`, `maple_nghia_pro.py`, `spotify_c2_runtime_support.py`; abort on any other source/config/evidence change.
- [ ] Private metadata identifies version `9.9.3`, variant `C2RuntimeParity`; do not modify repository stable manifest.
- [ ] README states that 20–50 / 50–150 is a runtime-supported candidate, only C2 uses it, and runtime parity still requires A/B validation.
- [ ] Run all V9.9.3 tests GREEN.
- [ ] Commit: `build: add deterministic V9.9.3 C2 runtime parity overlay`.

---

### Task 7: Windows Private Preflight

**Files:** create `.github/workflows/preflight-v9.9.3-c2-runtime-parity.yml`.

- [ ] Download public V9.9.2 Portable and fail unless SHA matches `7359f223339bf857fcbe68c7df036d6857cfe7b81a49ce76d5a217001f8a10b4`.
- [ ] Extract, snapshot source/evidence hashes, apply V9.9.3 overlay, verify allowed-only diff.
- [ ] Run the full historical regression matrix used by the last green PirateParity+RecoveredAPI preflight, then all V9.9.3 tests, `compileall`, and import smoke including `spotify_c2_runtime_support`.
- [ ] Rebuild with the same Nuitka one-file command as V9.9.2 and explicitly include `spotify_c2_runtime_support`.
- [ ] Reject `_MEIPASS` and `pyiboot01_bootstrap` markers.
- [ ] Run the real Windows default-launch smoke.
- [ ] Package `NghiaClient_V9.9.3_C2RuntimeParity_Portable.zip`, `NghiaEdition_Update_v9.9.3_C2RuntimeParity.zip`, `preflight_hashes.txt`, `preflight_report.json`.
- [ ] Report must include actual test count/hashes plus `version=9.9.3`, `variant=C2RuntimeParity`, `failures=0`, `errors=0`, base V9.9.2 SHA, action `[20,50]`, wait `[0.05,0.15]`, outer `[0.2,0.5]`, owner `C2`, `dynamic_combo_active=false`, `public_publish_performed=false`.
- [ ] Upload artifact `v9.9.3-c2-runtime-parity-preflight` only. Workflow must contain no `gh release create` and must not write `latest.json`.
- [ ] Commit: `ci: add V9.9.3 C2 runtime parity private preflight`.

---

### Task 8: Verification Before Completion

- [ ] Require every preflight step green: base hash, overlay, allowed diff, regression, V9.9.3 tests, compile/import, Nuitka, marker rejection, launcher smoke, package verification, artifact upload, publication lock.
- [ ] Download artifact, run `ZipFile.testzip()` on outer/Portable/Update, recompute hashes, compare with report.
- [ ] Re-check protected file hashes inside final Portable.
- [ ] Require final source markers `_spotify_c2_tp_skill_hold_combo`, `SPOTIFY_R54_COMBO_SPAM_ACTION_MS`, `SPOTIFY_R54_COMBO_SPAM_WAIT_S`, `owner="C2"`, `C2PauseReasons`, `C2RuntimeTraceBuffer`; require no `c2_fast_supervisor_pause`.
- [ ] Report only `Static/CI C2 runtime-parity candidate complete`. Do not claim Spotify runtime parity until same-machine A/B evidence. Reference runtime targets: median about `0.633 s`, mean about `0.637 s`, p90 about `0.743 s`.

## Self-Review

- Spec coverage: Tasks 1–8 cover timing, ownership, pause reasons, focus preservation, tracing, protected profiles, private preflight, and runtime-evidence boundary.
- Placeholder scan: no TBD/TODO/ellipsis implementation placeholders remain.
- Signature consistency: orchestrator owner is `SUPERVISOR` by default and `C2` for the C2 worker; pause helper names are consistent across plan tasks.
