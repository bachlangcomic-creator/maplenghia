from __future__ import annotations

import ast
import sys
from pathlib import Path

APP = Path(sys.argv[1] if len(sys.argv) > 1 else "portable/app_payload").resolve()


def method(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    return f"<missing {name}>"


def context(path: Path, needle: str, radius: int = 18) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if needle in line:
            lo = max(0, i - radius)
            hi = min(len(lines), i + radius + 1)
            return "\n".join(f"{n+1:05d}: {lines[n]}" for n in range(lo, hi))
    return f"<missing context {needle}>"

pro = APP / "maple_nghia_pro.py"
strategy = APP / "nghia_strategy_v10.py"
ui = APP / "nghia_spotify_nologin.py"

for name in [
    "build_simple_map_profile",
    "build_pirate_map_profile",
    "_spotify_mainfarm_sell_safe_stage",
    "_run_miumiu_sell_worker",
    "run_sell_thread",
    "_build_custom_map_panel",
    "_capture_custom_map_point",
    "save_custom_map",
]:
    print(f"\n===== PRO::{name} =====")
    print(method(pro, name))

for name in ["build_v10_pirate_profile", "resolve_v10_profile", "start", "tick"]:
    print(f"\n===== STRATEGY::{name} =====")
    print(method(strategy, name))

for needle in [
    '"LEFT", "RIGHT", "SAFE"',
    '"SAFE": "SAFE"',
    'BOTTOM LOOT',
    'notify_sell_completed',
    'MiuMiu parity hoàn tất',
    '10.0.15',
]:
    print(f"\n===== CONTEXT::{needle} =====")
    for path in (pro, strategy, ui):
        block = context(path, needle)
        if not block.startswith("<missing"):
            print(f"--- {path.name} ---")
            print(block)

print("\n===== V1017_BASE_INSPECTION_DONE =====")
