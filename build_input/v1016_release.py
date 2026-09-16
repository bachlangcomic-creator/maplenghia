from __future__ import annotations

VERSION = "10.0.16"
OLD_VERSION = "10.0.15"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_CustomSafeEntryReturn_Windows.zip"


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
            "V10.0.16 adds optional SAFE ENTRY and FARM RETURN coordinates only for Custom Map Strategy V10. "
            "Timed MiuMiu selling can route to SAFE ENTRY, use Up+Jump to reach SAFE, sell, then route to FARM RETURN "
            "and use Down+Jump to return to the farm lane. Upper-floor Fall Recovery can also use FARM RETURN. "
            "Original C1/C2/B1/B3/Pirate2 routes and protected Spotify core/maps remain unchanged."
        ),
    }
