# Nghia Client v10.0.14 — Sell Trigger Arbitration

Base: **v10.0.13 Custom Map Sell-Safe**.

Changes:
- Fixes MiuMiu Auto Sell stealing movement/skill input before the configured timer is actually due.
- When **Hẹn giờ bán MiuMiu** is enabled, only `spotify_sell_timer_event` can start the `SELL_SAFE` stage.
- `spotify_full_bag_event` and legacy `sell_only_when_full=False` state can no longer make timer mode jump/run toward SAFE early.
- When timer mode is disabled, full-bag detection remains the separate sell trigger.
- Toggling the Compact UI **Tự động bán đồ (MiuMiu)** switch clears stale full-bag/timer events and resets the watchdog sell schedule, so enabling Auto Sell does not immediately inherit an old trigger.

Preserved from v10.0.13:
- Custom Map `STRATEGY_V10` still uses the existing `SELL_SAFE` flow once the valid trigger is due: release farm inputs → move/verify `SAFE_PLACE` → run existing MiuMiu seller → resume farm.
- Watchdog preview type fix, SIMPLE/NONE optional bottom-loot coordinates, Custom Map parity features, Adaptive Y, Anti-Jitter/Hysteresis, STOP Non-Blocking, combat/TP/loot behavior, MiuMiu seller and CAPTCHA client-area capture are preserved.
- Bundled `maps.json`, Spotify recovered core, behavior engine and Strategy V10 farm logic remain unchanged except for the sell-trigger arbitration boundary described above.

Stable publication requires the 5 new trigger-arbitration tests, V10.0.13/V10.0.12/V10.0.11/V10.0.10/V10.0.9 regressions, Adaptive Y, STOP, all 17 Anti-Jitter regressions, compileall, fresh Windows/Nuitka build, PE verification, launcher smoke, updater package-contract verification, published updater hash verification, and only then promotion of stable `latest.json` to `10.0.14`.
