# Nghia Client v10.0.12 — Watchdog Preview Type Fix

Base: **v10.0.11 SIMPLE Loot Optional Coordinates**.

Changes:
- Fixes the watchdog/annotated-preview crash `cannot unpack non-iterable SpotifyDetectionResult object`.
- Recovered Spotify detector results remain logic evidence only and are no longer stored in caches that the preview interprets as `(score, x, y, w, h)` boxes.
- Adds a defensive preview-box type guard for `cached_full`, `cached_dead`, `cached_dc`, and `cached_captcha` before any coordinate unpacking.
- The exact detector/watchdog result flow itself is unchanged; only the preview cache typing boundary is corrected.

Preserved from v10.0.11:
- SIMPLE/NONE Custom Map loot modes do not require the four BOTTOM LOOT coordinates.
- `PIRATE_BOTTOM_CUSTOM` and legacy Pirate routes keep their existing coordinate requirements.
- V10.0.10 Custom Map parity features, MiuMiu timer/selling flow, CAPTCHA 1280x720 client-area capture, C2/B3 Adaptive Y, Anti-Jitter/Hysteresis, STOP Non-Blocking, combat/TP/loot behavior, and `maps.json` are preserved.

Stable publication requires the new V10.0.12 regression, V10.0.11/V10.0.10/V10.0.9 regressions, Adaptive Y, STOP, all 17 Anti-Jitter regressions, compileall, fresh Windows/Nuitka build, PE verification, rebuilt + packaged launcher smoke, published updater hash verification, and only then promotion of stable `latest.json` to `10.0.12`.
