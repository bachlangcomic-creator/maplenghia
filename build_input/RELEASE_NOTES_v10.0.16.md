# Nghia Client v10.0.16 — Custom Safe Entry + Farm Return

Base: **v10.0.15 Human Rest 1000–1500 ms**.

Changes:
- V10 Custom Map builder now exposes five farm coordinates: **LEFT / RIGHT / SAFE ENTRY / SAFE / FARM RETURN**.
- `SAFE ENTRY` is optional and isolated to V10 Custom Map profiles. When MiuMiu sell is due: farm input is released → the character moves to SAFE ENTRY → performs **UP + Jump** → moves/verifies SAFE → existing MiuMiu seller runs.
- `FARM RETURN` is optional and isolated to V10 Custom Map profiles. After a successful MiuMiu sale, the character moves to FARM RETURN → performs **DOWN + Jump** → waits for the farm-lane Y → resumes LEFT/RIGHT farming.
- When V10 Custom Map B1/B3 Fall Recovery detects a sustained upper-floor drift and FARM RETURN is configured, FARM RETURN owns recovery so combat does not fight the return route.
- Existing Custom Maps without SAFE ENTRY/FARM RETURN keep the previous behavior.

Preserved:
- **Bundled/original map profiles are unchanged** (`maps.json` SHA-256 unchanged).
- C1/C2/B1/B3/Pirate2 protected Spotify/core behavior is unchanged.
- V10.0.15 Human Rest remains 1000–1500 ms with the same 2% rest / 6% jump / 92% continue split.
- V10.0.14 MiuMiu Sell Trigger Arbitration is preserved.
- Adaptive Y, Anti-Jitter/Hysteresis, STOP Non-Blocking, loot/TP/skill behavior remain preserved outside the new V10 Custom Map route.

Stable publication requires V10.0.16 feature tests, the V10.0.15→V10.0.9 regression chain, Adaptive Y, STOP, all 17 Anti-Jitter regressions, compileall, fresh Windows/Nuitka build, PE verification, launcher smoke, updater package-contract verification, published updater hash verification, and only then promotion of stable `latest.json` to `10.0.16`.
