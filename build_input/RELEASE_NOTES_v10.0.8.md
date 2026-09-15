# Nghia Client v10.0.8 — Map-Aware Adaptive Y Toggle

Base: **v10.0.7 Anti-Jitter / Hysteresis Stable**.

This release exposes the existing Adaptive Y behavior as a visible map-aware ON/OFF control in the real Compact UI.

Changes:
- `C2`: checkbox controls the existing `c2_adaptive_y_enabled` path. ON keeps the current median/confidence Adaptive Y behavior; OFF uses the fixed profile Y.
- `B3`: the same checkbox controls the existing `b3_adaptive_y_enabled` path. ON locks the current runtime lane Y; OFF uses the fixed profile Y.
- Other maps: the Adaptive Y checkbox is disabled and shows that the feature does not apply.
- Toggling while the bot is running updates `runtime_cfg` immediately and clears the previous Adaptive Y anchor so the selected mode takes effect cleanly.
- The existing C2/B3 Adaptive Y engines are not rewritten.

Preserved from v10.0.7:
- Anti-Jitter / Hysteresis behavior and OFF bypass.
- STOP Non-Blocking.
- Loot Parity Defense and Pirate route-owned Loot.
- SIMPLE combat/TP/Skill cadence.
- `maps.json` coordinates and launcher/update protocol.

Release validation requires Adaptive Y tests, STOP regression, all 17 Anti-Jitter regressions, Python compileall, a fresh Windows/Nuitka build, PE verification, launcher smoke, packaged launcher smoke, published-asset hash verification, and only then promotion of stable `latest.json` to `10.0.8`.
