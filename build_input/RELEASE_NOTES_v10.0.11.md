# Nghia Client v10.0.11 — SIMPLE Loot Optional Coordinates

Base: **v10.0.10 Custom Map Parity**.

Changes:
- For **V10 PIRATE ROUTE** custom maps with `Loot = SIMPLE`, the four BOTTOM LOOT coordinates are no longer required.
- `Loot = NONE` also no longer requires BOTTOM LOOT coordinates.
- The BOTTOM LOOT buttons are disabled when the selected V10 loot mode does not use them, and the UI states that only `LEFT / RIGHT / SAFE` are required.
- `Loot = PIRATE_BOTTOM_CUSTOM` still requires all four BOTTOM LOOT points exactly as before.
- Legacy `PIRATE ROUTE` remains unchanged and still requires all four BOTTOM LOOT points.
- V10 profile serialization omits bottom-loot fields entirely for SIMPLE/NONE, matching the existing resolver/runtime semantics.

Preserved from v10.0.10:
- SIMPLE Human Behavior, B1/B3-style Fall Recovery, Spotify-style Loot Jitter, and Custom Map Adaptive Y.
- MiuMiu sell timer and CAPTCHA 1280x720 client-area capture.
- C2/B3 Adaptive Y, Anti-Jitter/Hysteresis, STOP Non-Blocking, and existing combat/TP/loot behavior.
- Bundled `maps.json` and protected Spotify/core files are unchanged.

Stable publication requires the V10.0.11 feature tests, V10.0.10/V10.0.9 regressions, Adaptive Y, STOP, all 17 Anti-Jitter regressions, compileall, fresh Windows/Nuitka build, PE verification, rebuilt + packaged launcher smoke, published updater hash verification, and only then promotion of stable `latest.json` to `10.0.11`.
