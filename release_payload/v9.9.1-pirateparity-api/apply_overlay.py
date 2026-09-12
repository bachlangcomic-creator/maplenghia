from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

BASE_BEHAVIOR_SHA = "3a6cc1e9ffaaae036c8625706aead23f5f85305a1a9de1165167240c9cae89db"
PATCHED_BEHAVIOR_SHA = "de137e5486518d183e26b83d360fa4a164e0fd136ce1deef003d6ad7b953fe97"
API_SHA = "1ceb0d194d1edfcab1a8005ac7fdd04343a90ff6962dc77d2dc675aac06a4339"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_overlay.py <portable-root>")

    root = Path(sys.argv[1]).resolve()
    behavior = root / "app_payload/spotify_behavior_engine.py"
    got = sha256(behavior)
    if got != BASE_BEHAVIOR_SHA:
        raise SystemExit(f"base behavior hash mismatch: {got} != {BASE_BEHAVIOR_SHA}")

    text = behavior.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "from spotify_recovered_core import SpotifyRecoveredCore\n",
        "from spotify_recovered_core import SpotifyRecoveredCore\nfrom spotify_recovered_api import SpotifyRecoveredAPI\n",
        "api-import",
    )
    text = replace_once(
        text,
        "        self.core = SpotifyRecoveredCore(host)\n",
        "        self.core = SpotifyRecoveredCore(host)\n        self.api = SpotifyRecoveredAPI(self.core)\n",
        "api-init",
    )
    old_dispatch = '''    def _dispatch_movement(self, cfg: dict, map_pos: MapPosition, now: float) -> bool:\n        kind = self.profile_kind(cfg)\n        if kind == "NONE":\n            return False\n        if kind == "STAND_STILL":\n            return bool(self.core._spotify_stand_still_step(cfg, map_pos, now))\n        if kind == "BUNNY":\n            return bool(self.core._spotify_bunny_step(cfg, map_pos, now))\n        if kind == "PIRATE2_1HIT":\n            return bool(self.core._spotify_pirate_step(cfg, map_pos, now, one_hit=True))\n        if kind == "PIRATE2":\n            return bool(self.core._spotify_pirate_step(cfg, map_pos, now, one_hit=False))\n        return bool(self.core._spotify_left_right_step(cfg, map_pos, now))\n'''
    new_dispatch = '''    def _dispatch_movement(self, cfg: dict, map_pos: MapPosition, now: float) -> bool:\n        kind = self.profile_kind(cfg)\n        if kind == "NONE":\n            return False\n        return bool(self.api.dispatch(kind, cfg, map_pos, now))\n'''
    text = replace_once(text, old_dispatch, new_dispatch, "api-dispatch")
    behavior.write_text(text, encoding="utf-8", newline="\n")

    source = Path(__file__).with_name("spotify_recovered_api.py")
    target = root / "app_payload/spotify_recovered_api.py"
    shutil.copyfile(source, target)

    got_behavior = sha256(behavior)
    got_api = sha256(target)
    if got_behavior != PATCHED_BEHAVIOR_SHA:
        raise SystemExit(f"patched behavior hash mismatch: {got_behavior} != {PATCHED_BEHAVIOR_SHA}")
    if got_api != API_SHA:
        raise SystemExit(f"API hash mismatch: {got_api} != {API_SHA}")

    print("V991_PIRATEPARITY_RECOVERED_API_OVERLAY_OK")


if __name__ == "__main__":
    main()
