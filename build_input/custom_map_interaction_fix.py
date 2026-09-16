from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()
TARGET = ROOT / "nghia_strategy_v10.py"
EXPECTED_PRE_FIX = "4fab9f9469b8e8fcd374410985688f8b0bde92923ad7e5561e2eb26a562a5f81"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


got = sha(TARGET)
if got != EXPECTED_PRE_FIX:
    raise SystemExit(f"unexpected pre-interaction-fix strategy hash {got}")

text = TARGET.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
old = '''        if resolved.tp_mode == "ADAPTIVE_Y" or self._custom_flag("CUSTOM_ADAPTIVE_Y"):\n            self._adaptive_y_step(cfg, map_pos, now)\n        elif resolved.tp_mode in {"ROUTE_TP", "SPAM_TP_SKILL"}:\n            self._teleport_step(cfg, map_pos, now)\n        self._fall_recovery_step(cfg, map_pos, now)\n        self._combat_step(cfg, map_pos, now, edge_hit=edge_hit)\n'''
new = '''        movement_action = False\n        if resolved.tp_mode == "ADAPTIVE_Y" or self._custom_flag("CUSTOM_ADAPTIVE_Y"):\n            movement_action = bool(self._adaptive_y_step(cfg, map_pos, now))\n        elif resolved.tp_mode in {"ROUTE_TP", "SPAM_TP_SKILL"}:\n            movement_action = bool(self._teleport_step(cfg, map_pos, now))\n        if not movement_action:\n            self._fall_recovery_step(cfg, map_pos, now)\n        self._combat_step(cfg, map_pos, now, edge_hit=edge_hit)\n'''
if text.count(old) != 1:
    raise SystemExit("interaction arbitration anchor mismatch")
text = text.replace(old, new, 1)
TARGET.write_bytes(text.encode("utf-8"))
print("V1010_INTERACTION_FIX_OK", sha(TARGET))
