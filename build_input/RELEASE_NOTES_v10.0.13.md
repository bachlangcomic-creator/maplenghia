# Nghia Client v10.0.13 — Custom Map Sell-Safe

Base: **v10.0.12 Watchdog Preview Type Fix**.

Changes:
- Custom Map `STRATEGY_V10` now consumes the existing Spotify `SELL_SAFE` stage before loot/farm.
- With **Tự động bán đồ (MiuMiu)** enabled and the sell timer due, Strategy V10 releases combat/movement, navigates to the Custom Map `SAFE_PLACE`, verifies arrival, and hands off to the existing MiuMiu seller.
- While `spotify_sell_inflight` is true or `sell_lock` is held, Strategy V10 stays paused and keeps its owned movement/skill inputs released.
- After the existing seller completes and releases ownership, Custom Map farming resumes automatically.
- No new Auto Sell toggle was added; V10.0.13 reuses the existing Auto Sell / timer settings and the Custom Map SAFE coordinate.

Preserved from v10.0.12:
- Watchdog preview `SpotifyDetectionResult` type fix.
- V10 Custom Map SIMPLE/NONE optional bottom-loot coordinates.
- SIMPLE Human Behavior, Fall Recovery, Loot Jitter, Custom Adaptive Y, C2/B3 Adaptive Y, Anti-Jitter/Hysteresis, STOP Non-Blocking, combat/TP/loot behavior, MiuMiu seller and CAPTCHA client-area capture.
- Bundled `maps.json` and protected Spotify/core files remain unchanged.

Stable publication requires the new Custom Map Sell-Safe regressions, V10.0.12/V10.0.11/V10.0.10/V10.0.9 regressions, Adaptive Y, STOP, all 17 Anti-Jitter regressions, compileall, fresh Windows/Nuitka build, PE verification, launcher smoke, updater package-contract verification, published updater hash verification, and only then promotion of stable `latest.json` to `10.0.13`.
