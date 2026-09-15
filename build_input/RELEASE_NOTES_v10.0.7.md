# Nghia Client v10.0.7 — Anti-Jitter / Hysteresis Stable

Base: **v10.0.6 Anti-Jitter / Hysteresis Candidate**.

This release promotes the already validated Anti-Jitter / Hysteresis candidate to semantic version **10.0.7** so clients already on **10.0.6** receive the update through the normal stable updater.

Runtime behavior is intentionally unchanged from the validated candidate:
- optional Anti-Jitter / Hysteresis toggle;
- OFF remains a true bypass to the original decision path;
- ON uses 2 consecutive edge samples, a 0.40 s turn lock, and 8 px departure hysteresis;
- Anti-Jitter does not own input and fails open;
- STOP Non-Blocking, Loot Parity Defense, Pirate route Loot, SIMPLE combat/TP/Skill cadence, maps and updater behavior are preserved.

The release workflow requires exact protected-source hashes, a provenance check proving the UI source differs from the V10.0.6 candidate only by semantic version digits, release-metadata tests, STOP regression coverage, all 17 Anti-Jitter regressions, Python compileall, a fresh Windows/Nuitka build, PE verification, launcher smoke, packaged launcher smoke, published-asset hash verification, and only then promotion of stable `latest.json` to `10.0.7`.
