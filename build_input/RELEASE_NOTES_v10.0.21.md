# Nghia Client v10.0.21 — TWO FLOOR Pass Count

Base: **Nghia Client v10.0.20 — TWO FLOOR ROUTE + Edit Custom Map**.

Changes:
- Adds **Số lượt mỗi tầng** to TWO FLOOR ROUTE, selectable from **1 to 10** and defaulting to **1**.
- One pass is counted only after the character travels from one configured lane edge to the opposite edge.
- The first edge reached after START or after entering a floor only arms the counter; it does **not** count as a completed pass by itself.
- The bot changes floor only after the configured number of completed passes.
- When the floor transition succeeds, the pass counter and edge origin reset for the new floor.
- Existing V10.0.20 profiles remain compatible: an old `TWO_FLOOR_CHANGE_EACH_LEG=true` profile maps to 1 pass; `false` maps to 2 passes when the new field is absent.
- Edit Custom Map loads and saves the new pass-count value.

Preserved:
- V10.0.20 TWO FLOOR verified-Y transitions, recovery, up/down modes, and Edit/Save/Cancel custom-map flow.
- V10.0.19 CAPTCHA `LIE_B64` multi-scale detection + clean-frame latch.
- V10.0.18 MiuMiu strict verified selling.
- Bundled `maps.json`, recovered Spotify core, CAPTCHA/watchdog, MiuMiu seller, and PC alarm remain hash-guarded.

Validation before stable promotion:
- V10.0.21 pass-count tests plus inherited V10.0.20/V10.0.19/V10.0.18/V10.0.16/V10.0.15/V10.0.14/V10.0.13/Adaptive-Y/STOP regressions.
- compileall, protected hashes, fresh Windows/Nuitka build, PE verification, launcher smoke, packaged smoke, updater contract, and published updater SHA verification.
- `latest.json` is promoted only after all prior checks succeed.
