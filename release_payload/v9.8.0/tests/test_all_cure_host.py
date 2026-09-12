import ast
import os
from pathlib import Path

APP = Path(os.environ.get("APP_PAYLOAD", Path(__file__).resolve().parents[3]))


def _text():
    return (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")


def _fn(name):
    text = _text(); tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(name)


def test_market_worker_is_host_owned_and_config_defaults_off():
    text = _text()
    assert "from spotify_all_cure_market import SpotifyAllCureMarketWorker" in text
    assert "self.spotify_all_cure_market = SpotifyAllCureMarketWorker(self)" in text
    assert "self.spotify_all_cure_market_enabled = tk.BooleanVar(value=False)" in text
    assert '"spotify_all_cure_market_enabled": bool(self.spotify_all_cure_market_enabled.get())' in text


def test_market_lifecycle_stops_before_combat_shutdown():
    start = _fn("start_bot")
    stop = _fn("stop_bot")
    assert "spotify_all_cure_market.start(cfg)" in start
    assert stop.index("spotify_all_cure_market.stop()") < stop.index("behavior_engine.stop()")


def test_market_bridge_is_fail_closed_and_releases_inputs_first():
    src = _fn("_spotify_market_run_action")
    assert "behavior_engine.release_inputs()" in src
    assert "return False" in src
    assert "pydirectinput.click" not in src
    assert "moveTo(" not in src


def test_f3_f7_roles_are_wired_but_c2_remains_isolated():
    hot = _fn("poll_hotkeys")
    assert '"F3"' in hot and "request_sell" in hot
    assert '"F7"' in hot and "spotify_all_cure_market_enabled" in hot
    c2 = _fn("_c2_fast_farm_worker").lower()
    for forbidden in ("all_cure", "market", '"f3"', '"f7"'):
        assert forbidden not in c2
