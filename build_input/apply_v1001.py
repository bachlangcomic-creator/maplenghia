from pathlib import Path
import hashlib

ROOT = Path('portable/app_payload')
BASE = {
    'spotify_recovered_core.py': '18e164944d5842629af55ca0f70f274192421515c01ac6451c0bdedf13109d95',
    'maple_nghia_pro.py': '203ac9e103ae3d7e441f7021d15e975e2a3cddaebed4ef8f2a53c17730c0e8bc',
    'nghia_spotify_nologin.py': '378d7bfcd4c9bd3cbc5e86fe23851e4cd6f399c823afc31ed60e83783ad92bb1',
    'nghia_strategy_v10.py': '6066d1ec948b7e9783944a1c2825a033061b1e130fde44b3799783263b1da9b8',
    'maps.json': '52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d',
}
OUT = {
    'spotify_recovered_core.py': '82054ca8057970f86510a7bcc89d1441e5c5d61185a9194d078083aee30ab90a',
    # C2/B3 Y behavior is intentionally byte-identical to V10.0.0.
    'maple_nghia_pro.py': BASE['maple_nghia_pro.py'],
    'nghia_spotify_nologin.py': '525eebc3eab0e8fc4375f935315d400ee4921784c07d240c7594bb68e4af3bbd',
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

for name, expected in BASE.items():
    got = sha(ROOT / name)
    assert got == expected, (name, got, expected)

core = ROOT / 'spotify_recovered_core.py'
t = core.read_text(encoding='utf-8')
old = '''            if lost_for >= max(SPOTIFY_R54_LOST_POSITION_LEFT_FLASH_UNTIL_S,\n                               SPOTIFY_RECOVERY_POSITION_SOFT):\n                self._spotify_recovery(cfg, now, f"mất minimap {lost_for:.1f}s")\n            if lost_for >= SPOTIFY_RECOVERY_POSITION_HARD and int(\n                    getattr(self, "spotify_recovery_stage", 0) or 0) < 3:\n                self._spotify_recovery(cfg, now, f"mất minimap kéo dài {lost_for:.1f}s")\n'''
new = '''            if bool(cfg.get("spotify_runtime_parity_mode", True)):\n                # Spotify stability parity: the recovered worker owns the 3.0s\n                # random_move stage. Do not run Nghia's fallback recovery in the\n                # same tick; only fall back if tracking is still lost at the hard\n                # timeout.\n                if lost_for >= SPOTIFY_RECOVERY_POSITION_HARD:\n                    self._spotify_recovery(\n                        cfg, now, f"mất minimap kéo dài {lost_for:.1f}s")\n            else:\n                # Preserve the legacy/non-parity safety policy.\n                if lost_for >= max(SPOTIFY_R54_LOST_POSITION_LEFT_FLASH_UNTIL_S,\n                                   SPOTIFY_RECOVERY_POSITION_SOFT):\n                    self._spotify_recovery(cfg, now, f"mất minimap {lost_for:.1f}s")\n                if lost_for >= SPOTIFY_RECOVERY_POSITION_HARD and int(\n                        getattr(self, "spotify_recovery_stage", 0) or 0) < 3:\n                    self._spotify_recovery(\n                        cfg, now, f"mất minimap kéo dài {lost_for:.1f}s")\n'''
assert old in t and new not in t
t = t.replace(old, new, 1)
core.write_text(t, encoding='utf-8', newline='\n')

# Do NOT alter maple_nghia_pro.py: C2/B3 Nghia Adaptive-Y policy stays exactly V10.0.0.
maple = ROOT / 'maple_nghia_pro.py'
text = maple.read_text(encoding='utf-8')
assert 'self.c2_adaptive_y_enabled = tk.BooleanVar(value=True)' in text
assert 'self.b3_adaptive_y_enabled = tk.BooleanVar(value=False)' in text
assert 'cfg.get("c2_adaptive_y_enabled", True)' in text
assert 'cfg.get("b3_adaptive_y_enabled", False)' in text

ui = ROOT / 'nghia_spotify_nologin.py'
t = ui.read_text(encoding='utf-8')
assert '10.0.0' in t and '10.0.1' not in t
t = t.replace('10.0.0', '10.0.1')
ui.write_text(t, encoding='utf-8', newline='\n')

for name, expected in OUT.items():
    got = sha(ROOT / name)
    assert got == expected, (name, got, expected)
for name in ('nghia_strategy_v10.py', 'maps.json'):
    assert sha(ROOT / name) == BASE[name], name
print('V1001_TRANSFORM_OK_Y_PRESERVED')
