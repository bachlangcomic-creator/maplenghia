# Nghia V10.0.0 Strategy Engine Design

## Goal

V10.0.0 makes new maps configurable without writing Python for each map. A map profile chooses its farm route, combat strategy, teleport strategy, and loot strategy independently, while existing maps continue to behave exactly as they do in V9.9.8 when the new fields are absent.

The first supported custom Pirate workflow is: define `LEFT`, `RIGHT`, `SAFE`, `LOOT_BOT_LEFT`, `LOOT_BOT_RIGHT`, `LOOT_BOT_1`, and `LOOT_BOT_2` in Map Builder, then choose existing combat/TP/loot strategies for that map.

## Scope

V10.0.0 adds profile-driven strategy selection for map execution. It does not invent new low-level combat or teleport behavior; it exposes existing proven behaviors as selectable strategies. It also does not copy Pirate 2 top-loot coordinates into custom Pirate maps.

Existing C1/C2/B1/B3, Pirate 2, and Pirate 2-1Hit behavior must remain backward compatible. Missing strategy fields on an existing profile resolve to the current legacy behavior for that map type.

## Profile schema

New optional fields:

```json
{
  "FARM_TYPE": "PIRATE_ROUTE",
  "COMBAT_MODE": "SPOTIFY_COMBO",
  "TP_MODE": "SPAM_TP_SKILL",
  "LOOT_MODE": "PIRATE_BOTTOM_CUSTOM"
}
```

Supported `COMBAT_MODE` values for V10.0.0:

- `LEGACY` — preserve the map type's current behavior.
- `SPOTIFY_COMBO` — use the recovered Spotify-style combat strategy already present in the engine.
- `HOLD_SKILL_1` — hold Skill 1 using the existing supported input path.
- `SPAM_SKILL` — use the existing repeated-skill strategy.
- `PIRATE_1HIT` — use the existing Pirate one-hit combat strategy.
- `STAND_STILL` — attack without route movement where the current engine supports it.

Supported `TP_MODE` values for V10.0.0:

- `LEGACY` — preserve current map behavior.
- `NONE` — do not invoke teleport behavior.
- `ROUTE_TP` — use route-owned teleport movement.
- `SPAM_TP_SKILL` — use the existing repeated teleport + skill strategy.
- `ADAPTIVE_Y` — use the current Adaptive-Y recovery/teleport behavior.

Supported `LOOT_MODE` values for V10.0.0:

- `LEGACY` — preserve current map behavior.
- `NONE` — no automatic loot route.
- `SIMPLE` — use the existing simple loot behavior where supported.
- `PIRATE_BOTTOM_CUSTOM` — use the map profile's four bottom-loot points.

Unknown values are invalid and must not silently fall back to another strategy.

## Map Builder changes

The existing coordinate builder keeps the SIMPLE workflow unchanged. For a new configurable map it adds three selectors: Combat, Teleport, and Loot.

When `LOOT_MODE=PIRATE_BOTTOM_CUSTOM`, the builder requires and saves these coordinates:

- `LOOT_BOT_LEFT_X/Y`
- `LOOT_BOT_RIGHT_X/Y`
- `LOOT_BOT_1_X/Y`
- `LOOT_BOT_2_X/Y`

A custom Pirate profile also requires `LEFT_X/Y`, `RIGHT_X/Y`, and `SAFE_PLACE_X/Y` for farm/recovery movement.

The builder validates required coordinates before saving. It must not fabricate missing coordinates from Pirate 2.

## Strategy resolution

At START, the engine resolves one immutable execution profile for the selected map. Resolution happens before worker dispatch so the worker does not repeatedly reinterpret strings from `maps.json`.

Resolution order:

1. Load the selected map profile.
2. Resolve `FARM_TYPE`.
3. Resolve `COMBAT_MODE`, `TP_MODE`, and `LOOT_MODE`.
4. Apply legacy defaults only when a strategy field is absent or explicitly `LEGACY`.
5. Validate that the selected strategies have all required coordinates/settings.
6. If validation succeeds, dispatch the existing worker with resolved strategies.
7. If validation fails, do not start the unsafe/incomplete route; show a precise error naming the missing or invalid field.

This keeps map selection/configuration separate from low-level key, skill, teleport, and loot implementations.

## Farm and combat behavior

Farm routing and combat remain separate responsibilities. A custom map can therefore use its own `LEFT/RIGHT/SAFE` route while selecting an existing combat strategy.

For example, Pirate 3 may use:

```text
FARM_TYPE=PIRATE_ROUTE
COMBAT_MODE=SPOTIFY_COMBO
TP_MODE=SPAM_TP_SKILL
LOOT_MODE=PIRATE_BOTTOM_CUSTOM
```

The engine must not select Pirate 2 solely because the map is Pirate-like. `PIRATE_ROUTE` is the configurable route family; Pirate 2 and Pirate 2-1Hit retain their existing legacy dispatch when their profiles do not opt into the new strategy fields.

## Custom Pirate bottom loot

`PIRATE_BOTTOM_CUSTOM` uses the selected map's own profile points only.

Forward pass:

```text
LOOT_BOT_LEFT -> LOOT_BOT_1 -> LOOT_BOT_2 -> LOOT_BOT_RIGHT
```

Reverse pass:

```text
LOOT_BOT_RIGHT -> LOOT_BOT_2 -> LOOT_BOT_1 -> LOOT_BOT_LEFT
```

The route alternates direction using the same route-state concept as the current Pirate bottom-loot behavior.

Custom Pirate maps do not run Pirate 2 top loot in V10.0.0. Top loot remains owned by the existing Pirate 2/Pirate 2-1Hit legacy route until a future builder explicitly captures top-loot coordinates for custom maps.

## Backward compatibility

Backward compatibility is a release blocker.

Profiles without `COMBAT_MODE`, `TP_MODE`, or `LOOT_MODE` must resolve to the same behavior they had in V9.9.8. Existing Pirate 2/Pirate 2-1Hit route-owned loot and timing must remain unchanged. Existing SIMPLE maps must continue to use their current SIMPLE route without requiring new fields.

No migration of existing `maps.json` entries is required.

## Error handling

Configuration errors are fail-closed for the affected strategy:

- Unknown strategy enum: block START for that map and show the invalid value.
- Missing required custom-loot coordinate: block START and name the missing field.
- Missing custom farm route point: block START and name the missing field.
- Legacy profile with no new strategy fields: continue normally.

Runtime failures inside an existing strategy keep that strategy's current recovery behavior; V10.0.0 does not add a second competing recovery loop.

## UI/version behavior

The visible application identity becomes `Nghia Edition V10.0.0`. `version.json`, local version fallbacks, build package names, and preflight reports use `10.0.0`.

Map Builder shows the three strategy selectors only in the configurable-map workflow so the current SIMPLE flow stays compact.

## Implementation boundaries

The change should introduce small resolver/validation helpers instead of adding more map-name conditionals to the worker loop.

Expected responsibilities:

- Map Builder: capture coordinates and strategy choices; save profile.
- Profile resolver: normalize legacy/default values and reject unknown modes.
- Validator: enforce fields required by the selected route/loot strategy.
- Farm dispatcher: select existing route family.
- Combat dispatcher: invoke the selected existing combat strategy.
- TP dispatcher: invoke the selected existing teleport strategy.
- Loot dispatcher: invoke legacy loot or custom bottom-loot route.

Existing low-level input/timing implementations are reused rather than duplicated.

## Testing

Tests are required before implementation changes are accepted.

Regression tests:

- C1/C2/B1/B3 profiles without new fields resolve to their legacy behavior.
- Pirate 2 profile without new fields keeps current combat, TP, bottom/top loot, and timing dispatch.
- Pirate 2-1Hit keeps its current route and one-hit behavior.

Strategy tests:

- A custom `PIRATE_ROUTE` profile resolves independently selected combat, TP, and loot modes.
- `PIRATE_BOTTOM_CUSTOM` reads points from the selected map, not Pirate 2 defaults.
- Forward and reverse custom bottom-loot ordering are correct.
- Custom Pirate route never invokes Pirate 2 top loot.
- Missing one required coordinate blocks dispatch with a precise validation error.
- Unknown strategy names block dispatch.
- `LEGACY` and absent fields produce the same resolved behavior for existing maps.

Build verification:

- `compileall` passes.
- Source/feature tests pass on Windows runner.
- Nuitka onefile build succeeds.
- Launcher smoke succeeds before packaging.
- Packaged candidate smoke succeeds after extraction.
- Candidate reports `10.0.0` and contains the expected strategy fields/UI labels.

## Release boundary

The first deliverable is a Windows V10.0.0 candidate. It is not published to `latest.json` and does not replace the current public release until the candidate is tested on real maps and explicitly approved for publishing.
