import ctypes
import os
import sys
import threading
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = Path(os.environ.get("NGHIA_APP_DIR", str(ROOT / "app_payload"))).resolve()
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from spotify_miumiu_sell import SpotifyMiuMiuSeller

MATCH = (0.99, 10, 20, 30, 40)


class SellerOwner:
    def __init__(self):
        self.running = True
        self.logs = []
        self.mouse_calls = []
        self.esc_calls = []

    def _log(self, text):
        self.logs.append(text)

    def _spotify_mouse_click_screen(self, cfg, x, y, **kwargs):
        self.mouse_calls.append((x, y, kwargs))
        return True

    def _game_has_focus(self, cfg):
        return True

    def _focus_game(self, cfg):
        return True

    def release_move(self):
        return None

    def _release_all_owned_inputs(self):
        return None

    def _press_input_key(self, key, hold_ms=0):
        self.esc_calls.append((key, hold_ms))
        return True


def cfg():
    return {
        "region": (100, 200, 1280, 720),
        "pause_on_focus_loss": True,
        "use_fast_capture": True,
        "current_map": "C2",
    }


def test_miumiu_card_uses_exactly_two_clicks_and_other_clicks_default_single(monkeypatch):
    owner = SellerOwner()
    seller = SpotifyMiuMiuSeller(owner)

    waits = iter([
        ("MIUMIU_OPENED_B64", MATCH),
    ])
    monkeypatch.setattr(seller, "_wait", lambda *a, **k: next(waits))

    assert seller._open_miumiu_shop(cfg(), MATCH, require_running=False) is True
    assert len(owner.mouse_calls) == 1
    assert owner.mouse_calls[0][2]["click_count"] == 2

    owner.mouse_calls.clear()
    assert seller._click(cfg(), MATCH) is True
    assert len(owner.mouse_calls) == 1
    assert owner.mouse_calls[0][2]["click_count"] == 1


def _import_maple_module(monkeypatch):
    class DummyUser32:
        def __getattr__(self, name):
            return lambda *a, **k: 1

    monkeypatch.setattr(ctypes, "windll", types.SimpleNamespace(user32=DummyUser32()), raising=False)
    sys.modules.pop("maple_nghia_pro", None)
    import maple_nghia_pro
    return maple_nghia_pro


class FakePyAutoGUI:
    def __init__(self):
        self.moves = []
        self.downs = []
        self.ups = []

    def moveTo(self, x, y, duration=0):
        self.moves.append((x, y, duration))

    def mouseDown(self, button="left"):
        self.downs.append(button)

    def mouseUp(self, button="left"):
        self.ups.append(button)


def _bare_maple_owner(mod, focus_sequence=None):
    owner = object.__new__(mod.MapleNghiaPro)
    owner.behavior_engine = types.SimpleNamespace(input_lock=threading.RLock())
    owner._last_input_error = ""
    owner._focus_game = lambda _cfg: True
    seq = list(focus_sequence or [True, True, True, True])

    def passive_focus(_cfg):
        if seq:
            return seq.pop(0)
        return True

    owner._game_has_focus = passive_focus
    return owner


def test_mouse_moves_once_for_double_click(monkeypatch):
    mod = _import_maple_module(monkeypatch)
    fake = FakePyAutoGUI()
    monkeypatch.setattr(mod, "PYAUTOGUI_AVAILABLE", True)
    monkeypatch.setattr(mod, "pyautogui", fake)
    monkeypatch.setattr(mod.time, "sleep", lambda _s: None)

    owner = _bare_maple_owner(mod, [True, True])
    ok = owner._spotify_mouse_click_screen(
        cfg(), 400, 300,
        move_ms=(0, 0), hold_ms=(0, 0),
        click_count=2, inter_click_ms=(0, 0),
    )
    assert ok is True
    assert len(fake.moves) == 1
    assert len(fake.downs) == 2
    assert len(fake.ups) == 2


def test_miumiu_open_retries_once_then_succeeds(monkeypatch):
    owner = SellerOwner()
    seller = SpotifyMiuMiuSeller(owner)
    clicks = []

    monkeypatch.setattr(seller, "_click", lambda *a, **k: clicks.append(k.get("click_count", 1)) or True)

    calls = {"opened": 0, "card": 0}
    def fake_wait(_cfg, names, **kwargs):
        if names == "MIUMIU_OPENED_B64":
            calls["opened"] += 1
            return (None, None) if calls["opened"] == 1 else ("MIUMIU_OPENED_B64", MATCH)
        if names == "MIUMIU_B64":
            calls["card"] += 1
            return "MIUMIU_B64", MATCH
        raise AssertionError(names)

    monkeypatch.setattr(seller, "_wait", fake_wait)
    monkeypatch.setattr("spotify_miumiu_sell.time.sleep", lambda _s: None)

    assert seller._open_miumiu_shop(cfg(), MATCH, require_running=False) is True
    assert clicks == [2, 2]
    assert calls["card"] == 1


def test_miumiu_open_fails_after_two_attempts(monkeypatch):
    owner = SellerOwner()
    seller = SpotifyMiuMiuSeller(owner)
    clicks = []
    monkeypatch.setattr(seller, "_click", lambda *a, **k: clicks.append(k.get("click_count", 1)) or True)

    def fake_wait(_cfg, names, **kwargs):
        if names == "MIUMIU_OPENED_B64":
            return None, None
        if names == "MIUMIU_B64":
            return "MIUMIU_B64", MATCH
        raise AssertionError(names)

    monkeypatch.setattr(seller, "_wait", fake_wait)
    monkeypatch.setattr("spotify_miumiu_sell.time.sleep", lambda _s: None)

    assert seller._open_miumiu_shop(cfg(), MATCH, require_running=False) is False
    assert clicks == [2, 2]


def test_missing_confirm_fails_sale(monkeypatch):
    owner = SellerOwner()
    seller = SpotifyMiuMiuSeller(owner)
    monkeypatch.setattr(seller, "_wait", lambda *a, **k: ("SELL_EQUIP_B64", MATCH))
    monkeypatch.setattr(seller, "_click", lambda *a, **k: True)
    monkeypatch.setattr(seller, "_click_confirm_and_verify", lambda *a, **k: False, raising=False)
    assert seller._sell_bulk_current_tab(cfg(), require_running=False) is False


def test_confirm_must_disappear(monkeypatch):
    owner = SellerOwner()
    seller = SpotifyMiuMiuSeller(owner)
    monkeypatch.setattr(seller, "_wait", lambda *a, **k: ("CONFIRM_B64", MATCH))
    monkeypatch.setattr(seller, "_click", lambda *a, **k: True)
    monkeypatch.setattr(seller, "_wait_until_absent", lambda *a, **k: False)
    assert seller._click_confirm_and_verify(cfg(), require_running=False) is False


def test_etc_failure_propagates_to_run(monkeypatch):
    owner = SellerOwner()
    seller = SpotifyMiuMiuSeller(owner)

    monkeypatch.setattr(seller, "_find_any", lambda *a, **k: ("CASH_TAB_2_B64", MATCH))
    monkeypatch.setattr(seller, "_wait", lambda _cfg, names, **kwargs: (str(names), MATCH))
    monkeypatch.setattr(seller, "_open_miumiu_shop", lambda *a, **k: True, raising=False)
    monkeypatch.setattr(seller, "_click", lambda *a, **k: True)
    monkeypatch.setattr(seller, "_click_confirm_and_verify", lambda *a, **k: True, raising=False)
    monkeypatch.setattr(seller, "_sell_etc", lambda *a, **k: False)

    assert seller.run(cfg(), should_sell_etc=True, require_running=False) is False


def test_focus_loss_between_double_clicks_releases_mouse(monkeypatch):
    mod = _import_maple_module(monkeypatch)
    fake = FakePyAutoGUI()
    monkeypatch.setattr(mod, "PYAUTOGUI_AVAILABLE", True)
    monkeypatch.setattr(mod, "pyautogui", fake)
    monkeypatch.setattr(mod.time, "sleep", lambda _s: None)

    owner = _bare_maple_owner(mod, [True, False])
    ok = owner._spotify_mouse_click_screen(
        cfg(), 400, 300,
        move_ms=(0, 0), hold_ms=(0, 0),
        click_count=2, inter_click_ms=(0, 0),
    )
    assert ok is False
    assert len(fake.moves) == 1
    assert len(fake.downs) == 1
    assert len(fake.ups) >= 1


def test_pirate_etc_without_verified_sale_does_not_false_success(monkeypatch):
    owner = SellerOwner()
    seller = SpotifyMiuMiuSeller(owner)
    monkeypatch.setattr(seller, "_find_any", lambda *a, **k: (None, None))
    timeline = iter([0.0, 0.0, 3.1, 3.1])
    monkeypatch.setattr("spotify_miumiu_sell.time.monotonic", lambda: next(timeline, 3.1))
    monkeypatch.setattr("spotify_miumiu_sell.time.sleep", lambda _s: None)
    assert seller._sell_pirate_etc(cfg(), require_running=False) == "FAILED"
