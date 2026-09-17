# Nghia Client v10.0.23 — TWO FLOOR Natural Combat

Base: **Nghia Client v10.0.22 — TWO FLOOR SAFE UI**.

Fixes the movement regression reported on TWO FLOOR ROUTE:
- Horizontal travel toward `UP_POINT` / `DOWN_POINT` no longer owns and consumes the whole strategy tick.
- While travelling horizontally to a floor-transition point, the normal movement/teleport/combat pipeline continues, restoring the natural run + attack cadence inherited from V10.0.18.
- Combat direction is synchronized with the actual transition target, avoiding a stale left/right direction fighting the movement key.
- The edge tick that arms a floor change is no longer dropped; it can finish through the normal combat cadence before transition travel begins.
- If Y is genuinely off the transition lane, vertical correction remains safety-gated and does not mix an attack into that correction tick.
- `WAIT_TOP` / `WAIT_BOTTOM` still verify the target-floor Y before farming resumes, so the bot does not blindly farm the wrong floor.

Preserved unchanged:
- V10.0.22 TWO FLOOR SAFE UI and shared behavior/recovery/jitter options.
- V10.0.21 passes-per-floor counting.
- V10.0.20 Edit Map / TWO FLOOR coordinates and bounded transition recovery.
- V10.0.19 CAPTCHA Scale + Latch detection/alert behavior.
- V10.0.18 MiuMiu Strict sale flow.
- `spotify_recovered_core.py` and bundled `maps.json` are hash-protected and are not modified by this release.
