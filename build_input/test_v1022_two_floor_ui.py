from pathlib import Path
import os, sys

APP = Path(os.environ.get('NGHIA_APP_DIR', str(Path(__file__).resolve().parent / 'app_payload'))).resolve()
sys.path.insert(0, str(APP))


def test_two_floor_top_farm_section_only_needs_safe_points():
    from nghia_custom_map_profiles import builder_farm_safe_slots
    assert builder_farm_safe_slots('TWO FLOOR ROUTE') == ('SAFE_ENTRY', 'SAFE')
    assert builder_farm_safe_slots('SIMPLE') == ('LEFT', 'RIGHT', 'SAFE_ENTRY', 'SAFE')
    assert builder_farm_safe_slots('V10 PIRATE ROUTE') == ('LEFT', 'RIGHT', 'SAFE_ENTRY', 'SAFE')


def test_two_floor_profile_can_enable_fall_recovery():
    from nghia_strategy_v10 import build_v10_two_floor_profile
    profile = build_v10_two_floor_profile(
        (10,100),(90,100),(10,60),(90,60),(90,100),(10,60),(50,40),
        loot_mode='NONE', custom_fall_recovery=True,
    )
    assert profile['CUSTOM_FALL_RECOVERY'] is True


def test_two_floor_ui_wires_shared_safety_options_and_safe_only_top_section():
    text = (APP / 'maple_nghia_pro.py').read_text(encoding='utf-8')
    assert 'builder_farm_safe_slots' in text
    assert 'custom_fall_recovery=custom_fall_recovery.get()' in text
    assert 'TWO FLOOR: SAFE ENTRY/SAFE' in text
