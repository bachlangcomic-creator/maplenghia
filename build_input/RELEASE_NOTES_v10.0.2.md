Nghia V10.0.2 makes the Codex Fix 10.0.1 runtime the canonical Nghia base.

- Preserves Codex farm/combat timing and Strategy V10 behavior.
- Keeps C1/C2/B1/B3, TP/Skill, Adaptive Y, Pirate/Bunny/Stand routes unchanged from the canonical Codex base.
- Keeps thread-local capture, revive state machine, Buff/Loot retry backoff, and worker heartbeat/restart supervision.
- Fixes the WorkerSupervisor generation race where a stale worker exit could mark the current generation as expected-stop.
- Strategy V10 and maps.json remain unchanged.

Stable promotion only happens after Windows/Nuitka build, launcher smoke, packaged smoke, and source integrity guards pass.
