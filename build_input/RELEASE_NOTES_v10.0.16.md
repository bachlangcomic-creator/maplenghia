# Nghia Client v10.0.16 — Custom Safe Entry

Base: **v10.0.15 Human Rest 1000–1500 ms**.

Changes:
- Custom Map builder adds an optional **SAFE ENTRY** coordinate next to LEFT / RIGHT / SAFE.
- SAFE ENTRY is saved only when the user captures it. Existing Custom Maps without SAFE ENTRY remain compatible and keep the previous direct-SAFE sell flow.
- When MiuMiu sell is due on a Custom Map with SAFE ENTRY: farm input is released → move to SAFE ENTRY → perform **UP + configured Jump key** → short settle → move/verify SAFE → run the existing MiuMiu seller.
- SAFE ENTRY is implemented at the Custom Map sell-routing boundary; bundled/original map profiles do not gain the new field.
- **FARM RETURN is not included in v10.0.16**. Post-sell return routing will be handled as a separate later change.

Preserved:
- Bundled `maps.json` is byte-for-byte unchanged.
- C1/C2/B1/B3/Pirate2 original profiles and protected Spotify/core behavior are unchanged.
- V10.0.15 Human Rest remains 1000–1500 ms with the same 2% rest / 6% jump / 92% continue split.
- V10.0.14 MiuMiu Sell Trigger Arbitration is preserved.
- Adaptive Y, Anti-Jitter/Hysteresis, STOP Non-Blocking, loot/TP/skill behavior remain preserved outside the optional Custom Map SAFE ENTRY route.

Stable publication requires the V10.0.16 SAFE ENTRY feature tests, the V10.0.15→V10.0.9 regression chain, Adaptive Y, STOP, all 17 Anti-Jitter regressions, compileall, fresh Windows/Nuitka build, PE verification, launcher smoke, updater package-contract verification, published updater hash verification, and only then promotion of stable `latest.json` to `10.0.16`.
