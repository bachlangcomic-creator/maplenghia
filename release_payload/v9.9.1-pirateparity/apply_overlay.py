from __future__ import annotations

import hashlib
import sys
from pathlib import Path

BASE_HASHES = {
    "app_payload/spotify_recovered_core.py": "56aac0ffc721e47b62af852310a688fc3561a72b3e8cdc614a74124eb19973a4",
    "app_payload/maple_nghia_pro.py": "7555afa8904c8a29d8cfd473cea428cb52c4d92e3012fd98812d709474beed38",
}
PATCHED_HASHES = {
    "app_payload/spotify_recovered_core.py": "961ee533f03c01a9fd2b62f58900ad8af7b7a8aabcca3612d25b1f21adb42019",
    "app_payload/maple_nghia_pro.py": "85c05cfb2645fb756f5a644564972b59388c5d39e385f439b3065d369dc8142d",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(data: bytes, old: bytes, new: bytes, label: str) -> bytes:
    count = data.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return data.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_overlay.py <portable-root>")
    root = Path(sys.argv[1]).resolve()

    for rel, want in BASE_HASHES.items():
        path = root / rel
        got = sha256(path)
        if got != want:
            raise SystemExit(f"base hash mismatch {rel}: {got} != {want}")

    core = root / "app_payload/spotify_recovered_core.py"
    data = core.read_bytes()
    data = replace_once(
        data,
        (
            '        """UI gate for all SpotifyRecoveredCore loot paths.\r\n\r\n'
            '        This does not re-enable any Nghĩa loot worker; it only decides whether\r\n'
            '        SpotifyRecoveredCore is allowed to enter its recovered loot schedules.\r\n'
            '        """'
        ).encode("utf-8"),
        (
            '        """UI gate for generic SpotifyRecoveredCore loot paths.\r\n\r\n'
            '        This does not re-enable any Nghĩa loot worker; it only decides whether\r\n'
            '        SpotifyRecoveredCore is allowed to enter its generic loot schedules.\r\n'
            "        Pirate2's top/bottom route is intentionally independent of this toggle.\r\n"
            '        """'
        ).encode("utf-8"),
        "generic-loot-docstring",
    )
    data = replace_once(
        data,
        (
            '        # The compact Nghĩa UI exposes a Loot checkbox. It gates the recovered\r\n'
            '        # Pirate2 top/bottom routes without handing control back to Nghĩa.\r\n'
            '        if not self._spotify_loot_enabled(cfg):\r\n'
            '            if self.spotify_pirate_state in {"TOP_LOOT", "LOOTING_BOT_1", "LOOTING_SWEEP", "LOOTING_BOT_2"}:\r\n'
            '                self.release_move()\r\n'
            '                self._spotify_reset_move_to_state()\r\n'
            '                self.spotify_pirate_state = "FARM"\r\n'
            '                self.spotify_pirate_top_substate = "MOVE_TOP"\r\n'
            '                self.spotify_pirate_loot_substate = "TO_START"\r\n'
            '                self.spotify_pirate_phase_started = 0.0\r\n'
            '            return False\r\n\r\n'
        ).encode("utf-8"),
        (
            "        # Spotify's Pirate routines own their top/bottom loot schedules directly.\r\n"
            '        # The Nghĩa Auto Loot checkbox only gates generic loot on other profiles;\r\n'
            "        # it must not disable Pirate2's built-in route state machine.\r\n\r\n"
        ).encode("utf-8"),
        "pirate-loot-gate",
    )
    core.write_bytes(data)

    ui = root / "app_payload/maple_nghia_pro.py"
    data = ui.read_bytes()
    data = replace_once(
        data,
        (
            '        # V9.3 UI toggle: this controls SpotifyRecoveredCore loot scheduling.\r\n'
            '        # It is NOT the old Nghĩa generic auto-loot worker.\r\n'
        ).encode("utf-8"),
        (
            '        # This gates generic Spotify loot on non-Pirate profiles.\r\n'
            '        # Pirate2 owns its top/bottom route and always runs it internally.\r\n'
        ).encode("utf-8"),
        "ui-loot-comment",
    )
    ui.write_bytes(data)

    for rel, want in PATCHED_HASHES.items():
        path = root / rel
        got = sha256(path)
        if got != want:
            raise SystemExit(f"patched hash mismatch {rel}: {got} != {want}")

    print("V991_PIRATEPARITY_OVERLAY_OK")


if __name__ == "__main__":
    main()
