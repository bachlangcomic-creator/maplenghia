# Nghia Client v10.0.19 — CAPTCHA Scale + Latch

Base: **Nghia Client v10.0.18 — MiuMiu Strict Sell**.

Changes:
- Keeps Spotify forensic alarm trigger on **`LIE_B64`** only; `QUESTION_CAPTCHA_1_B64/2_B64` are not independent alarm triggers.
- CAPTCHA `LIE_B64` matching now checks scales **0.90, 0.95, 1.00, 1.05, 1.10** inside Nghia's existing CAPTCHA ROI, with the recovered threshold **0.70**.
- Adds a CAPTCHA state latch: `ABSENT → APPEARED → PRESENT → CLEARED`.
- Alarm/pause fires once on `APPEARED`; repeated matching frames do not create repeated alert threads.
- CAPTCHA pause is removed only after **3 consecutive clean frames**, so brief detector flicker does not prematurely resume farming.
- The watchdog now forwards unmatched CAPTCHA scan results so the `CLEARED` transition can actually be observed.

Preserved:
- V10.0.18 MiuMiu verified double-click + strict Confirm flow.
- Existing PC alarm parameters (`2000 Hz`, `300 ms`, `3` repeats) are unchanged.
- SAFE ENTRY / Return To Farm, maps, farm movement, loot, TP, skills, MiuMiu, and recovered core behavior are unchanged outside CAPTCHA detection/transition handling.

Validation before stable promotion:
- V10.0.19 CAPTCHA regression tests.
- inherited V10.0.18/V10.0.16/V10.0.15/V10.0.14/V10.0.13/Adaptive-Y/STOP regressions.
- compileall, protected hashes, fresh Windows/Nuitka build, PE verification, launcher smoke, packaged smoke, updater contract, published updater hash verification.
- `latest.json` is promoted only after all prior checks succeed.
