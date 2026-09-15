# Nghia Client v10.0.6 — STOP Non-Blocking

Stable base: **v10.0.3 Loot Parity Defense**.

This release fixes the Nghia client freeze where pressing **STOP BOT** could wait indefinitely behind the shared `input_lock` while the hot farm worker continued to own/reacquire input.

Changes:
- STOP now invalidates farm/input producers immediately and returns control to the UI without waiting for `input_lock`.
- Blocking key release and worker joins run in a daemon cleanup phase.
- Behavior Engine, Strategy V10, Watchdog and All Cure workers expose lock-free stop requests.
- New input-down/press requests are fenced while STOP cleanup is active.
- START is briefly refused while the previous STOP cleanup is still finishing.

Preserved from v10.0.3:
- Loot Parity Defense.
- Pirate2/Pirate2 1-Hit route-owned Loot behavior.
- SIMPLE combat/TP/Skill cadence.
- maps.json coordinates, Adaptive Y, MiuMiu, revive and launcher/update protocol.
