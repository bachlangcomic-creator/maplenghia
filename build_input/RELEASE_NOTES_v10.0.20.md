# Nghia Client v10.0.20 — TWO FLOOR ROUTE + Edit Custom Map

Base: **Nghia Client v10.0.19 — CAPTCHA Scale + Latch**.

Changes:
- Adds **TWO FLOOR ROUTE** to Custom Map Builder.
- Captures `BOTTOM_LEFT`, `BOTTOM_RIGHT`, `TOP_LEFT`, `TOP_RIGHT`, `UP_POINT`, `DOWN_POINT`, plus existing `SAFE` / optional `SAFE_ENTRY`.
- Farms the current floor LEFT ↔ RIGHT, moves to the configured transition point, performs the selected vertical action, and only changes floor state after Y is verified near the target lane.
- Supports `JUMP_UP`, `TP_UP`, `JUMP_TP_UP` for going up and `DOWN_JUMP`, `DROP`, `TP_DOWN` for going down.
- Adds **Adaptive Y for TWO FLOOR ROUTE**, **Two Floor Recovery**, and **Change floor after each leg** options.
- A failed floor transition does not silently continue farming on the wrong floor; recovery is bounded and then fails safe.
- Adds **Edit Map**, **Save Changes**, and **Cancel Edit**. Existing custom maps can be loaded back into the builder, coordinates/options changed, renamed, and atomically saved without leaving the old name duplicated.

Preserved:
- V10.0.19 CAPTCHA `LIE_B64` multi-scale detection + 3-clean-frame latch.
- V10.0.18 MiuMiu verified double-click + strict Confirm flow.
- Bundled `maps.json`, Spotify recovered core, MiuMiu seller, CAPTCHA detector/watchdog, and PC alarm are hash-guarded against unintended changes.

Validation before stable promotion:
- V10.0.20 TWO FLOOR / map-edit tests.
- inherited V10.0.19/V10.0.18/V10.0.16/V10.0.15/V10.0.14/V10.0.13/Adaptive-Y/STOP regressions.
- compileall, protected hashes, fresh Windows/Nuitka build, PE verification, launcher smoke, packaged smoke, updater contract, published updater hash verification.
- `latest.json` is promoted only after all prior checks succeed.
