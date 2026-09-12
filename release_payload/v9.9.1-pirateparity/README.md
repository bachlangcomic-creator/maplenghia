# Nghia V9.9.1 PirateParity private overlay

This private overlay starts from the exact public `v9.9.1` Portable artifact and changes only Pirate loot ownership semantics:

- Pirate Den 2 and Pirate Den 2 1-Hit keep their recovered top/bottom loot schedules even when the generic Nghia Auto Loot checkbox is off.
- Generic non-Pirate loot remains gated by the existing Auto Loot toggle.
- C1/C2/B1/B3, Dynamic Combo, MiuMiu, All Cure, watchdog, focus, updater, launcher and evidence files remain unchanged.
- The application executable is rebuilt with Nuitka on Windows.

This workflow is private-preflight only. It does not publish a GitHub Release and does not update `latest.json`.
