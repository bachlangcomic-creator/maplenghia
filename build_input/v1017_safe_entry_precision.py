from __future__ import annotations

from pathlib import Path
import sys

MARKER = "V10.0.17_SAFE_ENTRY_PRECISION"


def apply(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return
    old = '''        reached = bool(self.behavior_engine.core._spotify_move_to_step(\n            cfg, map_pos, float(entry_x), float(entry_y), float(now),\n            tolerance_x=5.0, tolerance_y=8.0, check_stuck=False, flash_range=9999.0,\n        ))\n        if not reached:\n            return \"PENDING\"\n\n        self.behavior_engine.release_inputs()\n'''
    new = '''        # V10.0.17_SAFE_ENTRY_PRECISION\n        px, py = float(map_pos[0]), float(map_pos[1])\n        # Climb only after a tighter confirmation than generic move_to's 5/8px\n        # tolerance.  This prevents an early UP+Jump beside the rope/ladder.\n        if abs(px - float(entry_x)) > 2.0 or abs(py - float(entry_y)) > 4.0:\n            self.behavior_engine.core._spotify_move_to_step(\n                cfg, map_pos, float(entry_x), float(entry_y), float(now),\n                tolerance_x=2.0, tolerance_y=4.0, check_stuck=False, flash_range=9999.0,\n            )\n            return \"PENDING\"\n\n        self.behavior_engine.release_inputs()\n'''
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"SAFE ENTRY precision anchor expected once, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("V1017_SAFE_ENTRY_PRECISION_OK")


if __name__ == "__main__":
    app_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload")
    apply(app_dir / "maple_nghia_pro.py")
