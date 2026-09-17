# Nghia Client v10.0.22 — TWO FLOOR SAFE UI

Base: **Nghia Client v10.0.21 — TWO FLOOR Pass Count**.

Changes:
- When **TWO FLOOR ROUTE** is selected, the top `FARM / SAFE` block now shows only **SAFE ENTRY** and **SAFE**.
- Generic `LEFT` / `RIGHT` are no longer shown or requested in the TWO FLOOR builder; the route already uses **BOTTOM LEFT/RIGHT** and **TOP LEFT/RIGHT**.
- Internal compatibility `LEFT_X/RIGHT_X` is still derived from the bottom lane, so existing runtime code does not need extra user input.
- TWO FLOOR now exposes **SIMPLE Human Behavior**, **B1/B3 Fall Recovery**, and **Loot Jitter kiểu Spotify**.
- `B1/B3 Fall Recovery` is wired into TWO FLOOR using the engine's existing current-lane Y recovery path.
- Dedicated **Two Floor Recovery** remains separate and continues to handle failed UP/DOWN transitions.
- `SAFE ENTRY` remains optional; `SAFE` remains required for the MiuMiu/sell-safe flow.

Preserved:
- V10.0.21 `Số lượt mỗi tầng` (1–10) and full-crossing pass counter.
- V10.0.20 Edit/Save/Cancel Custom Map.
- V10.0.19 CAPTCHA Scale Latch.
- V10.0.18 MiuMiu Strict.
- Bundled `maps.json`, recovered Spotify core, CAPTCHA/watchdog, MiuMiu seller, and PC alarm remain hash-guarded.

Validation before stable promotion:
- New V10.0.22 tests plus inherited V10.0.21/V10.0.20/V10.0.19/V10.0.18/V10.0.16/V10.0.15/V10.0.14/V10.0.13/Adaptive-Y/STOP regressions.
- compileall, protected hashes, fresh Windows/Nuitka build, PE verification, launcher smoke, packaged smoke, updater contract, and published updater SHA verification.
- `latest.json` is promoted only after all prior checks succeed.
