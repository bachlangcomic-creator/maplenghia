# Nghia V9.9.3 – C2 Runtime Parity Design

## Context

V9.9.2 is the current public stable base. It already contains PirateParity, SpotifyRecoveredAPI, recovered focus/HWND caching, recovered main-farm stage metadata, MiuMiu/All Cure/watchdog parity work, and the shared SIMPLE-map `run_left_and_right` path.

Deeper forensic analysis of the original Spotify `main.dll` (SHA-256 `62860aeb8a80ac4a768aa8f3afafe23f079aa07e2981786e44989ad71b941cb0`) exposes two remaining C2 runtime-parity gaps:

1. Production C2 micro-timing in Nghia still uses the previously reconstructed `15..45 ms` TP→Skill gap and `125..255 ms` post-skill wait, while a separate Spotify timing family of `20..50 ms` key-holds plus `50..150 ms` pair wait reproduces the measured Spotify C2 runtime distribution far more closely.
2. Nghia C2 currently splits ownership between a dedicated Fast Worker and the supervisor/main-farm orchestrator, while Spotify exposes one `main_farm_worker` that owns pet/recovery/buffs/farm dispatch for SIMPLE profiles.

This design changes only the C2 runtime path. Other maps and protected subsystems stay behaviorally unchanged.

## Goal

Make C2 runtime behavior measurably closer to Spotify by correcting the C2 TP+Skill pair timing and giving one C2 worker sole ownership of the recovered main-farm stage sequence, without regressing focus safety, stop semantics, other farm profiles, selling, watchdog, All Cure, or updater behavior.

## Evidence Model

### Direct / runtime-validated evidence

- Spotify C2 video runtime: median about `0.6333 s`, mean about `0.6369 s`, p10 about `0.5667 s`, p90 about `0.7433 s` per observed movement/combat interval.
- Spotify embeds PyDirectInput behavior with effective `PAUSE=0.1 s` in the recovered package/runtime model.
- `Farm.left_and_right` is the SIMPLE-map path used by C1/C2/B1/B3.
- SIMPLE C2 uses an outer combo window of `200..500 ms` and a pre-combo delay of about `50 ms`.
- Spotify `__main__` exposes `watchdog_worker`, `session_monitor_worker`, `focus_enforcer_worker`, and `main_farm_worker`; there is no recovered `c2_fast_worker`/`Farm.c2` symbol.
- Recovered `main_farm_worker` stage order is `state_gate -> sell_safe -> pet -> lost_player_recovery -> buff1 -> buff2 -> farm_dispatch`.

### Runtime-supported C2 timing candidate

A Spotify timing family associated with the TP+Skill spam description contains:

- Teleport/Skill action hold: random `20..50 ms`.
- Wait after the TP+Skill pair: random `50..150 ms`.
- Pre-combo delay: about `50 ms`.

With PyDirectInput pause overhead, this produces a model centered around roughly `0.62 s`, which closely matches the measured Spotify C2 median around `0.633 s`.

By contrast, the current Nghia C2 combination (`45 ms` tap holds plus `15..45 ms` and `125..255 ms` sleeps) models near `0.76 s`, close to the older Nghia runtime mean. Therefore the `20..50 / 50..150` family is the preferred C2 runtime-parity candidate for this private build.

### Evidence that must remain separated

The `15..45 ms / 125..255 ms` constant family also appears around recovered random-movement/helper material. This design therefore does **not** rewrite global `hold_combo_action` semantics for every profile. The corrected timing is applied only to the C2 production runtime path until an A/B runtime trace validates it.

Dynamic Combo remains dormant. This design does not wire `perform_dynamic_combo` into production farming.

## Architecture

### 1. Single C2 main-farm owner

The existing high-frequency C2 minimap worker remains because it avoids putting full-screen preview/controller work on the hot path. Its responsibility changes from “movement-only Fast Worker” to “C2 Main Farm Owner”.

For each valid C2 farm tick, the owner executes the recovered stage sequence:

```text
state_gate
-> sell_safe
-> pet
-> lost_player_recovery
-> buff1
-> buff2
-> farm_dispatch
   -> SpotifyRecoveredAPI.run_left_and_right(...)
```

The supervisor remains responsible for preview/UI and non-farm monitoring but must not execute duplicate C2 pet/recovery/buff/farm-dispatch side effects while the C2 owner is active.

### 2. C2-only runtime combo primitive

C2 production combat receives a dedicated parity primitive rather than changing the shared SIMPLE/Pirate helper globally.

Conceptual contract:

```python
c2_runtime_combo(direction_key, flash_key, skill_key, hold_time_s)
```

Behavior:

1. Preserve the existing input ownership/stop-generation contract.
2. Hold movement direction through the existing input bridge.
3. Sleep the recovered pre-combo delay (~`0.05 s`) at the same caller boundary currently used by C2.
4. Until the outer combo window expires:
   - tap Teleport/Flash with random key hold `20..50 ms` if enabled;
   - tap Skill with random key hold `20..50 ms`;
   - sleep random `50..150 ms` after the pair.
5. Preserve PyDirectInput pause behavior; do not reduce global `PAUSE=0.1 s`.
6. Abort immediately on stop/generation invalidation and release all owned keys.
7. If Teleport is disabled/unconfigured, run Skill-only without inventing another timing family.

The outer C2 combo window remains random `0.200..0.500 s`.

### 3. Ownership and pause reasons

C2 input/farm ownership must be explicit. A single boolean that can be cleared by unrelated subsystems is not sufficient.

The C2 owner maintains pause reasons (set/clear semantics) for at least:

- `sell`
- `captcha`
- `disconnect`
- `revive`
- `all_cure`
- `stop`

C2 resumes only when no blocking reason remains. This prevents one subsystem from clearing another subsystem's pause and creating concurrent input.

### 4. Focus handling

Keep the V9.9.2 dedicated focus worker and cached HWND/focus state. Do not reintroduce per-combo `EnumWindows`/foreground enumeration into the C2 hot path.

C2 action code may read cached focus state and must release input immediately when the focus worker marks the game unsafe/unfocused.

### 5. Supervisor behavior while C2 owns farm

The supervisor may continue:

- preview/UI updates;
- watchdog state processing that does not directly send farm input;
- status rendering/logging;
- update/launcher bridge work.

It must not run C2 farm-side pet, recovery, buffs, generic farm dispatch, or duplicate movement/combat calls while the C2 owner is active.

## Protected Behavior

The following must not change in this feature:

- C1/B1/B3 production combo timing and routing.
- Pirate Den 2 normal and Pirate Den 2 1-Hit timing/state machines.
- Bunny and Stand Still.
- `SpotifyRecoveredAPI` public route inventory.
- Dynamic Combo dormant/evidence-gated status.
- MiuMiu seller state machine.
- All Cure workflow and template gating.
- Watchdog thresholds/sell scheduling/alarm behavior.
- Focus worker cadence/cache architecture.
- Maps, bounds, coordinates, and map thresholds.
- Launcher/update transaction behavior.
- Session exclusion and CAPTCHA detect/pause/alert-only policy.

C2 Adaptive Y remains a Nghia extension and is not used as timing evidence. Existing user config behavior is preserved.

## Failure / Recovery Semantics

- Lost focus: C2 owner releases keys and pauses farm dispatch.
- Sell begins: add `sell` pause reason before any seller input; remove only after seller completion/failure cleanup.
- CAPTCHA/disconnect/revive/All Cure: add their own independent pause reason before input takeover.
- Stop: invalidate the generation, add stop state, release all owned keys, and terminate C2 owner cleanly.
- Missing Skill key: fail closed for combat and surface the existing error/status path.
- Missing Teleport key or disabled Teleport: Skill-only path, no arbitrary fallback key.
- Any exception in C2 input: release direction/Teleport/Skill and return control to the owner loop without leaving a key held.

## Instrumentation for Runtime Validation

Private V9.9.3 builds add lightweight monotonic trace points that are disabled by default and can be enabled for A/B testing. Trace records must include:

- tick start/end;
- each main-farm stage start/end;
- C2 combo start/end;
- Teleport keyDown/keyUp timestamps;
- Skill keyDown/keyUp timestamps;
- pair-wait start/end;
- focus-safe state changes;
- pause-reason add/remove events.

The trace must not contain credentials or session data.

## Test Design

### RED tests first

Tests must fail on unmodified V9.9.2 for these contracts:

1. C2 owner stage trace equals exactly:
   `STATE -> SELL_SAFE -> PET -> RECOVERY -> BUFF1 -> BUFF2 -> DISPATCH`.
2. Supervisor does not run duplicate C2 pet/recovery/buff/dispatch while C2 owner is active.
3. C2 combo uses action-hold draws only in `20..50 ms` and pair-wait draws only in `50..150 ms`.
4. C2 keeps outer window `0.200..0.500 s` and pre-combo delay about `0.05 s`.
5. C1/B1/B3 still use their existing production helper/timing path.
6. Pirate normal/1-Hit paths remain unchanged.
7. Pause reasons compose correctly: clearing `sell` cannot resume while `captcha` is still present.
8. Stop/focus loss/input exceptions leave no owned keys held.
9. Dynamic Combo remains absent from active farm dispatch.

### Regression

Run the complete V9.7 -> V9.9.2 regression suite plus new V9.9.3 tests. Protected-source/hash guards should be used where practical to ensure unrelated evidence/timing files are unchanged.

### Windows preflight

Before any publication decision:

1. compile/import final payload;
2. run full regression suite;
3. rebuild the app with Nuitka one-file;
4. reject PyInstaller carry-over markers;
5. run real Windows launcher smoke;
6. package Portable and Update private artifacts;
7. verify hashes and required payload members;
8. upload a private preflight artifact only.

## Runtime Acceptance

Static/CI acceptance is necessary but not sufficient for claiming Spotify runtime parity.

For C2 runtime validation, collect at least one same-machine A/B sample with Spotify reference and the private Nghia build under equivalent game/config conditions. Preferred target:

- median C2 interval near Spotify's observed `~0.633 s`;
- mean near `~0.637 s`;
- p90 not materially worse than Spotify's observed `~0.743 s`;
- no new stuck-key, focus-loss, duplicate pet/buff/recovery, or seller-contention failures.

If the private build remains materially above about `0.65 s` median, instrumentation determines whether the residual gap comes from capture/detection, stage arbitration, scheduler contention, or input dispatch. Do not reduce PyDirectInput pause or unrelated recovered sleeps by guesswork.

## Release Strategy

This work starts as a private V9.9.3 candidate based on the exact public V9.9.2 implementation commit. It must not mutate existing v9.9.2 release assets or `main/latest.json`.

Public release requires a separate explicit user approval after private preflight and runtime evidence review.

## Acceptance Criteria

1. C2 alone uses the runtime-supported `20..50 ms` action-hold / `50..150 ms` pair-wait candidate.
2. C2 outer combo window remains `0.200..0.500 s`; pre-combo timing remains about `0.05 s`.
3. C2 has exactly one farm/input owner.
4. C2 stage order is `state -> sell_safe -> pet -> recovery -> buff1 -> buff2 -> dispatch`.
5. Supervisor cannot duplicate C2 farm side effects.
6. Focus remains worker/cache based, not hot-path window enumeration.
7. Pause reasons cannot clear each other incorrectly.
8. C1/B1/B3/Pirate/Bunny/Stand Still remain behaviorally unchanged.
9. Dynamic Combo remains dormant.
10. Full regression, Nuitka build, PyInstaller rejection, and Windows launcher smoke all pass.
11. Private artifacts are produced before any publication action.
12. Runtime parity is claimed only after A/B trace evidence, not from CI alone.
