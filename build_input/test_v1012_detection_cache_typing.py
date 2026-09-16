from pathlib import Path
import ast
import os

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload"))
SRC = APP / "maple_nghia_pro.py"


def _method_source(name: str) -> str:
    text = SRC.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    raise AssertionError(f"method not found: {name}")


def test_watchdog_detection_results_are_not_cached_as_preview_boxes():
    src = _method_source("_spotify_watchdog_scan_frame")
    assert "setattr(self, cache_name, recovered)" not in src
    assert "setattr(self, cache_name, None)" in src


def test_preview_only_unpacks_box_like_alert_cache_values():
    helper = _method_source("_preview_box_or_none")
    assert "isinstance(value, (tuple, list))" in helper
    preview = _method_source("bot_loop")
    assert "full = self._preview_box_or_none(self.cached_full)" in preview
    assert "_preview_box_or_none(self.cached_dead)" in preview
    assert "_preview_box_or_none(self.cached_dc)" in preview
    assert "_preview_box_or_none(self.cached_captcha)" in preview
