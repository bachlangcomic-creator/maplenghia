# Nghia Client v10.0.9 — MiuMiu Timer + CAPTCHA Client Capture

Base: **v10.0.8 Map-Aware Adaptive Y Toggle**.

Changes:
- Compact UI now exposes the existing Spotify MiuMiu timer with `Hẹn giờ bán MiuMiu` and a minute field (default 30).
- Toggling the timer or changing minutes updates `runtime_cfg` immediately while the bot is running.
- The Spotify sell scheduler itself is unchanged: for a 30-minute base value it keeps the recovered random window of 20–36 minutes.
- CAPTCHA watchdog capture now uses the cached Maple HWND client area. It converts the 1280x720 client origin to desktop coordinates and captures exactly that client rectangle instead of the configured full-desktop region.
- CAPTCHA detector thresholds/assets and PC alarm behavior are unchanged; this release fixes the frame source feeding them.

Preserved from v10.0.8:
- Map-aware Adaptive Y for C2/B3.
- Anti-Jitter / Hysteresis and OFF bypass.
- STOP Non-Blocking.
- Loot Parity Defense and Pirate route-owned Loot.
- SIMPLE combat/TP/Skill cadence.
- `maps.json` and updater protocol.

Release validation requires V10.0.9 feature tests, V10.0.8 Adaptive Y regressions, STOP regression, all 17 Anti-Jitter regressions, compileall, a fresh Windows/Nuitka build, PE verification, launcher smoke, packaged launcher smoke, published-asset hash verification, and only then promotion of stable `latest.json` to `10.0.9`.
