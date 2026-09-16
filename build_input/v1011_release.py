from __future__ import annotations

VERSION = "10.0.11"
OLD_VERSION = "10.0.10"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_SimpleLootOptional_Windows.zip"


def stable_manifest(sha256: str) -> dict[str, str]:
    package_url = (
        "https://github.com/bachlangcomic-creator/maplenghia/releases/"
        f"download/{TAG}/{UPDATE_ASSET}"
    )
    return {
        "version": VERSION,
        "channel": "stable",
        "package_url": package_url,
        "url": package_url,
        "sha256": sha256,
        "payload_dir": "app_payload",
        "min_launcher_version": "1.0.1",
        "notes": (
            "V10.0.11 keeps all V10.0.10 Custom Map parity features and makes bottom-loot "
            "coordinates optional for V10 Custom Maps when Loot is SIMPLE or NONE. "
            "PIRATE_BOTTOM_CUSTOM still requires all four bottom-loot coordinates."
        ),
    }
