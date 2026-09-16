# Nghia Client v10.0.15 — Human Rest 1000–1500 ms

Base: **v10.0.14 Sell Trigger Arbitration**.

Changes:
- Keeps SIMPLE Human Behavior probability split unchanged: **2% rest / 6% jump / 92% continue**.
- Changes Human Rest duration from **3–5 seconds** to **1000–1500 ms**.
- Human Rest remains non-blocking through `human_pause_until`; STOP responsiveness is preserved.
- Random jump remains unchanged at **150–300 ms**.

Preserved from v10.0.14 and earlier:
- MiuMiu Sell Trigger Arbitration.
- Custom Map `STRATEGY_V10` Sell-Safe → Custom Map `SAFE_PLACE` → existing MiuMiu seller → resume farm.
- Watchdog preview type fix, SIMPLE/NONE optional bottom-loot coordinates, Loot Jitter, Fall Recovery, Custom Adaptive Y, C2/B3 Adaptive Y, Anti-Jitter/Hysteresis, STOP Non-Blocking, combat/TP/loot behavior.
- Bundled `maps.json` and protected Spotify/core files remain unchanged.

Stable publication requires the new Human Rest regression tests, V10.0.14/V10.0.13/V10.0.12/V10.0.11/V10.0.10/V10.0.9 regressions, Adaptive Y, STOP, all 17 Anti-Jitter regressions, compileall, fresh Windows/Nuitka build, PE verification, launcher smoke, updater package-contract verification, published updater hash verification, and only then promotion of stable `latest.json` to `10.0.15`.
