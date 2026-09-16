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


def lines(path: Path, start: int, end: int) -> str:
    data = path.read_text(encoding="utf-8").splitlines()
    lo = max(1, start)
    hi = min(len(data), end)
    return "\n".join(f"{n:05d}: {data[n-1]}" for n in range(lo, hi + 1))

pro = APP / "maple_nghia_pro.py"
strategy = APP / "nghia_strategy_v10.py"
ui = APP / "nghia_spotify_nologin.py"
core = APP / "spotify_recovered_core.py"

for name in [
    "build_simple_map_profile",
    "build_pirate_map_profile",
    "_spotify_mainfarm_sell_safe_stage",
]:
    print(f"\n===== PRO::{name} =====")
    print(method(pro, name))

for name in ["build_v10_pirate_profile", "resolve_v10_profile", "start", "tick"]:
    print(f"\n===== STRATEGY::{name} =====")
    print(method(strategy, name))

for name in ["_spotify_move_to_step", "_spotify_jump_up", "_spotify_jump_down_reconstructed"]:
    print(f"\n===== CORE::{name} =====")
    print(method(core, name))

for needle in [
    '"LEFT", "RIGHT", "SAFE"',
    '"SAFE": "SAFE"',
    'BOTTOM LOOT',
    'build_simple_map_profile(',
    'build_pirate_map_profile(',
    'build_v10_pirate_profile(',
    'notify_sell_completed',
    'MiuMiu parity hoàn tất',
    '10.0.15',
]:
    print(f"\n===== CONTEXT::{needle} =====")
    for path in (pro, strategy, ui, core):
        block = context(path, needle, radius=28)
        if not block.startswith("<missing"):
            print(f"--- {path.name} ---")
            print(block)

print("\n===== STRATEGY HEAD 1..180 =====")
print(lines(strategy, 1, 180))
print("\n===== CUSTOM MAP BUILDER 2235..2495 =====")
print(lines(pro, 2235, 2495))
print("\n===== SELL WORKER 3490..3550 =====")
print(lines(pro, 3490, 3550))
print("\n===== V1017_BASE_INSPECTION_DONE =====")
