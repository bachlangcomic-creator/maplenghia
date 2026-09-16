from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

APP = Path(os.environ.get("NGHIA_APP_DIR", "portable/app_payload"))


def load_strategy():
    p = APP / "nghia_strategy_v10.py"
    spec = importlib.util.spec_from_file_location("nghia_strategy_v10_test", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_simple_profile_allows_missing_bottom_loot_coords():
    mod = load_strategy()
    profile = mod.build_v10_pirate_profile(
        (10, 20), (30, 20), (20, 20),
        None, None, None, None,
        "SPOTIFY_COMBO", "SPAM_TP_SKILL", "SIMPLE", 0.6,
    )
    assert profile["LOOT_MODE"] == "SIMPLE"
    for key in mod.BOTTOM_LOOT_FIELDS:
        assert key not in profile
    resolved = mod.resolve_v10_profile(profile)
    assert resolved.loot_left is None
    assert resolved.loot_right is None
    assert resolved.loot_1 is None
    assert resolved.loot_2 is None


def test_none_profile_allows_missing_bottom_loot_coords():
    mod = load_strategy()
    profile = mod.build_v10_pirate_profile(
        (10, 20), (30, 20), (20, 20),
        None, None, None, None,
        "SPOTIFY_COMBO", "SPAM_TP_SKILL", "NONE", 0.6,
    )
    assert profile["LOOT_MODE"] == "NONE"
    for key in mod.BOTTOM_LOOT_FIELDS:
        assert key not in profile


def test_pirate_bottom_still_requires_coords():
    mod = load_strategy()
    try:
        mod.build_v10_pirate_profile(
            (10, 20), (30, 20), (20, 20),
            None, None, None, None,
            "SPOTIFY_COMBO", "SPAM_TP_SKILL", "PIRATE_BOTTOM_CUSTOM", 0.6,
        )
    except Exception:
        return
    raise AssertionError("PIRATE_BOTTOM_CUSTOM must reject missing bottom-loot coordinates")


def test_builder_requires_bottom_coords_only_for_v10_pirate_bottom():
    s = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    assert 'needs_bottom_loot = is_pirate and (not is_v10 or loot_mode.get() == "PIRATE_BOTTOM_CUSTOM")' in s
    assert 'if needs_bottom_loot:' in s
    assert 'loot_left = captured["LOOT_LEFT"] if needs_bottom_loot else None' in s


def test_builder_disables_bottom_loot_controls_when_not_needed():
    s = (APP / "maple_nghia_pro.py").read_text(encoding="utf-8")
    assert 'def sync_loot_ui' in s
    assert 'state = "normal" if needs_bottom_loot else "disabled"' in s
    assert 'loot_mode_combo.bind("<<ComboboxSelected>>", sync_loot_ui)' in s
