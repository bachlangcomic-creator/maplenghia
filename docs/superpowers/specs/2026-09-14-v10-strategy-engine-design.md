# Nghia V10.0.0 Strategy Engine Design

## Goal

V10.0.0 makes new maps configurable without writing Python for each map. A new configurable map profile chooses its farm route, combat strategy, teleport strategy, and loot strategy independently.

Legacy maps are hard-isolated from the V10 Strategy Engine. C1/C2/B1/B3, Pirate 2, Pirate 2-1Hit, and any other profile without the explicit V10 opt-in flag continue through the existing V9.9.8 dispatch path and do not enter the new resolver, validator, combat dispatcher, TP dispatcher, or loot dispatcher.

The first supported custom Pirate workflow is: define `LEFT`, `RIGHT`, `SAFE`, `LOOT_BOT_LEFT`, `LOOT_BOT_RIGHT`, `LOOT_BOT_1`, and `LOOT_BOT_2` in Map Builder, then choose existing combat/TP/loot strategies for that map.

## Scope

V10.0.0 adds profile-driven strategy selection only for profiles that explicitly opt in. It does not invent new low-level combat or teleport behavior; it exposes existing proven behaviors as selectable strategies. It also does not copy Pirate 2 top-loot coordinates into custom Pirate maps.

Existing C1/C2/B1/B3, Pirate 2, Pirate 2-1Hit, and all other non-opted-in profiles must remain on the legacy code path. Their behavior is a release blocker and must not depend on any V10 strategy defaulting logic.

## Profile schema

New configurable maps use an explicit engine marker:

```json
{
  "ENGINE_MODE": "STRATEGY_V10",
  "FARM_TYPE": "PIRATE_ROUTE",
  "COMBAT_MODE": "SPOTIFY_COMBO",
  "TP_MODE": "SPAM_TP_SKILL",
  "LOOT_MODE": "PIRATE_BOTTOM_CUSTOM"
}
```

`ENGINE_MODE=STRATEGY_V10` is required to enter the new Strategy Engine. If the field is absent, empty, `LEGACY`, or any value other than the recognized V10 marker, the profile stays on the legacy dispatch path. Existing map profiles are not migrated automatically.

Supported `COMBAT_MODE` values for opted-in V10 profiles:

- `SPOTIFY_COMBO` — use the recovered Spotify-style combat strategy already present in the engine.
- `HOLD_SKILL_1` — hold Skill 1 using the existing supported input path.
- `SPAM_SKILL` — use the existing repeated-skill strategy.
- `PIRATE_1HIT` — use the existing Pirate one-hit combat strategy.
- `STAND_STILL` — attack without route movement where the current engine supports it.

Supported `TP_MODE` values for opted-in V10 profiles:

- `NONE` — do not invoke teleport behavior.
- `ROUTE_TP` — use route-owned teleport movement.
- `SPAM_TP_SKILL` — use the existing repeated teleport + skill strategy.
- `ADAPTIVE_Y` — use the current Adaptive-Y recovery/teleport behavior.

Supported `LOOT_MODE` values for opted-in V10 profiles:

- `NONE` — no automatic loot route.
- `SIMPLE` — use the existing simple loot behavior where supported.
- `PIRATE_BOTTOM_CUSTOM` — use the map profile's four bottom-loot points.

Unknown values on an opted-in V10 profile are invalid and must not silently fall back to another strategy. Legacy profiles do not interpret these fields at all because they never enter the V10 resolver.

## Map Builder changes

The existing SIMPLE workflow stays unchanged. Existing legacy profiles are not rewritten with V10 fields.

For a new configurable map, Map Builder creates `ENGINE_MODE=STRATEGY_V10` and shows three selectors: Combat, Teleport, and Loot.

When `LOOT_MODE=PIRATE_BOTTOM_CUSTOM`, the builder requires and saves these coordinates:

- `LOOT_BOT_LEFT_X/Y`
- `LOOT_BOT_RIGHT_X/Y`
- `LOOT_BOT_1_X/Y`
- `LOOT_BOT_2_X/Y`

A custom Pirate profile also requires `LEFT_X/Y`, `RIGHT_X/Y`, and `SAFE_PLACE_X/Y` for farm/recovery movement.

The builder validates required coordinates before saving. It must not fabricate missing coordinates from Pirate 2.

## Dispatch isolation gate

The START path checks `ENGINE_MODE` before any V10 logic runs.

- If `ENGINE_MODE != STRATEGY_V10`: call the existing V9.9.8 legacy dispatcher unchanged.
- If `ENGINE_MODE == STRATEGY_V10`: resolve and validate the configurable execution profile, then dispatch through the V10 strategy layer.

This gate is the compatibility boundary. The new strategy resolver must not be used to decide legacy behavior, and the V10 validator must never block a legacy map.

## Strategy resolution

Only after the opt-in gate passes does the engine resolve one immutable V10 execution profile for the selected map. Resolution happens before worker dispatch so the worker does not repeatedly reinterpret strings from `maps.json`.

Resolution order:

1. Confirm `ENGINE_MODE=STRATEGY_V10`.
2. Load the selected map profile.
3. Resolve `FARM_TYPE`.
4. Resolve `COMBAT_MODE`, `TP_MODE`, and `LOOT_MODE`.
5. Validate that the selected strategies have all required coordinates/settings.
6. If validation succeeds, dispatch the existing low-level behaviors through V10 strategy wrappers.
7. If validation fails, do not start the unsafe/incomplete route; show a precise error naming the missing or invalid field.

There is no V10 fallback-to-legacy strategy inside an opted-in profile. A bad opted-in profile fails closed rather than leaking into a legacy map implementation.

## Farm and combat behavior

Farm routing and combat remain separate responsibilities. A custom map can therefore use its own `LEFT/RIGHT/SAFE` route while selecting an existing combat strategy.

For example, Pirate 3 may use:

```text
ENGINE_MODE=STRATEGY_V10
FARM_TYPE=PIRATE_ROUTE
COMBAT_MODE=SPOTIFY_COMBO
TP_MODE=SPAM_TP_SKILL
LOOT_MODE=PIRATE_BOTTOM_CUSTOM
```

The engine must not select Pirate 2 solely because the map is Pirate-like. `PIRATE_ROUTE` is the configurable V10 route family. Pirate 2 and Pirate 2-1Hit remain on their existing legacy dispatcher unless a future explicit migration is designed and approved.

## Custom Pirate bottom loot

`PIRATE_BOTTOM_CUSTOM` uses the selected V10 map's own profile points only.

Forward pass:

```text
LOOT_BOT_LEFT -> LOOT_BOT_1 -> LOOT_BOT_2 -> LOOT_BOT_RIGHT
```

Reverse pass:

```text
LOOT_BOT_RIGHT -> LOOT_BOT_2 -> LOOT_BOT_1 -> LOOT_BOT_LEFT
```

The route alternates direction using the same route-state concept as the current Pirate bottom-loot behavior, but with separate V10 route state so it cannot mutate Pirate 2 legacy route state.

Custom Pirate maps do not run Pirate 2 top loot in V10.0.0. Top loot remains owned by the existing Pirate 2/Pirate 2-1Hit legacy route until a future builder explicitly captures top-loot coordinates for custom maps.

## Backward compatibility and legacy isolation

Backward compatibility is a release blocker.

Legacy maps are protected by all of these rules:

1. No `ENGINE_MODE=STRATEGY_V10` means the profile bypasses the new Strategy Engine completely.
2. No existing `maps.json` entry is automatically migrated or rewritten.
3. V10 resolver/validator errors cannot block C1/C2/B1/B3, Pirate 2, Pirate 2-1Hit, or other legacy profiles.
4. Pirate 2/Pirate 2-1Hit keep their current route-owned loot, top loot, timing, recovery, and combat dispatch.
5. SIMPLE maps keep their current route and input behavior without requiring any new fields.
6. V10 custom-route state is stored separately from legacy Pirate route state.
7. Existing low-level functions may be reused by V10 wrappers, but their legacy call sites, arguments, timing constants, and branch conditions are not changed merely to support V10.

No migration of existing `maps.json` entries is required.

## Error handling

Configuration errors are fail-closed only for opted-in V10 profiles:

- Unknown strategy enum: block START for that V10 map and show the invalid value.
- Missing required custom-loot coordinate: block START and name the missing field.
- Missing custom farm route point: block START and name the missing field.
- Missing or unrecognized `ENGINE_MODE`: do not enter V10; continue through legacy dispatch.

Runtime failures inside an existing low-level strategy keep that behavior's current recovery semantics; V10.0.0 does not add a second competing recovery loop to legacy maps.

## UI/version behavior

The visible application identity becomes `Nghia Edition V10.0.0`. `version.json`, local version fallbacks, build package names, and preflight reports use `10.0.0`.

Map Builder shows the three strategy selectors only in the new configurable-map workflow so the current SIMPLE/legacy flows stay compact and unchanged.

## Implementation boundaries

The change introduces a narrow opt-in gate plus small resolver/validation helpers instead of adding more map-name conditionals to the legacy worker loop.

Expected responsibilities:

- Legacy dispatcher: remains the authoritative path for all non-V10 profiles.
- Map Builder: capture coordinates and strategy choices for new V10 maps; save `ENGINE_MODE=STRATEGY_V10`.
- V10 profile resolver: interpret only opted-in profiles and reject unknown modes.
- V10 validator: enforce fields required by the selected route/loot strategy.
- V10 farm dispatcher: select configurable route family.
- V10 combat dispatcher: invoke the selected existing combat behavior.
- V10 TP dispatcher: invoke the selected existing teleport behavior.
- V10 loot dispatcher: invoke custom/simple/no-loot behavior for V10 profiles.

Existing low-level input/timing implementations are reused rather than duplicated, but legacy dispatch code remains independently callable and testable.

## Testing

Tests are required before implementation changes are accepted.

Legacy-isolation regression tests:

- C1/C2/B1/B3 without `ENGINE_MODE=STRATEGY_V10` call the same legacy dispatcher as V9.9.8.
- Pirate 2 without the V10 marker never enters the V10 resolver, validator, combat dispatcher, TP dispatcher, or loot dispatcher.
- Pirate 2 keeps current combat, TP, bottom/top loot, timing, and recovery dispatch.
- Pirate 2-1Hit keeps its current route and one-hit behavior and never enters V10.
- A legacy profile containing accidental `COMBAT_MODE`, `TP_MODE`, or `LOOT_MODE` fields but lacking the V10 engine marker still remains legacy.
- A V10 validation failure cannot prevent a subsequent legacy map from starting normally.
- V10 custom route direction/state changes do not alter Pirate 2 legacy loot direction/state.

V10 strategy tests:

- A custom `PIRATE_ROUTE` profile with `ENGINE_MODE=STRATEGY_V10` resolves independently selected combat, TP, and loot modes.
- `PIRATE_BOTTOM_CUSTOM` reads points from the selected map, not Pirate 2 defaults.
- Forward and reverse custom bottom-loot ordering are correct.
- Custom Pirate route never invokes Pirate 2 top loot.
- Missing one required coordinate blocks only that V10 profile with a precise validation error.
- Unknown strategy names block only that opted-in V10 profile.
- A profile without the V10 marker cannot accidentally activate the new engine even if strategy-like fields are present.

Build verification:

- `compileall` passes.
- Source/feature tests pass on Windows runner.
- All legacy-isolation tests pass before the candidate is accepted.
- Nuitka onefile build succeeds.
- Launcher smoke succeeds before packaging.
- Packaged candidate smoke succeeds after extraction.
- Candidate reports `10.0.0` and contains the expected V10 strategy fields/UI labels.

## Release boundary

The first deliverable is a Windows V10.0.0 candidate. It is not published to `latest.json` and does not replace the current public release until the candidate is tested on real maps and explicitly approved for publishing.
