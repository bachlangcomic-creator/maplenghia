# Nghia Client v10.0.17 — Custom SAFE ENTRY + Return To Farm

Base: **verified v10.0.15 Human Rest 1000–1500 ms stable asset**.

Changes:
- V10 Custom Map adds an optional **SAFE ENTRY** point alongside LEFT / RIGHT / SAFE.
- When a valid MiuMiu sell trigger is due and SAFE ENTRY is configured: farming input is released → character moves tightly to SAFE ENTRY → **UP + configured Jump** → existing SAFE navigation verifies SAFE → existing MiuMiu seller runs.
- After a successful MiuMiu sale, **RETURN TO FARM** reuses the same SAFE ENTRY X coordinate from the upper SAFE floor: align horizontally to `SAFE_ENTRY_X` → **DOWN + configured Jump** → confirm farm-lane Y → resume normal LEFT/RIGHT farming.
- RETURN TO FARM never tries to walk to the lower `SAFE_ENTRY_Y` while still on the upper SAFE floor.
- If post-sale farm-lane Y cannot be confirmed after bounded retries, the bot remains stopped instead of resuming farming on the wrong floor.
- Existing Custom Maps without SAFE ENTRY keep the previous direct-SAFE behavior.

Not included:
- The separate **FARM RETURN** / wrong-floor recovery coordinate discussed for accidental floor drift while farming is not part of v10.0.17.

Preserved:
- Bundled/original map profiles remain unchanged (`maps.json` SHA-256 unchanged).
- C1/C2/B1/B3/Pirate2 protected behavior is unchanged.
- v10.0.15 Human Rest timing, v10.0.14 MiuMiu Sell Trigger Arbitration, v10.0.13 Custom Map Sell-Safe, Adaptive Y, Anti-Jitter/Hysteresis, STOP Non-Blocking, loot/TP/skill behavior are preserved outside the new Custom Map route.

Stable publication requires the v10.0.17 feature tests, inherited v10.0.15→v10.0.9 regression chain, Adaptive Y, STOP, all 17 Anti-Jitter regressions, compileall, fresh Windows/Nuitka build, PE verification, launcher smoke, updater package-contract verification, packaged smoke, published updater hash verification, and only then promotion of stable `latest.json` to `10.0.17`.
