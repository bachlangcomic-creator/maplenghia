from __future__ import annotations

VERSION = "10.0.17"
BASE_VERSION = "10.0.15"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_SafeEntryReturn_Windows.zip"


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
            "V10.0.17 is rebuilt from the verified V10.0.15 stable base. "
            "V10 Custom Map adds optional SAFE ENTRY for MiuMiu selling: move to SAFE ENTRY, UP+Jump, then verify SAFE before selling. "
            "After a successful MiuMiu sale, RETURN TO FARM aligns to SAFE_ENTRY_X on the upper SAFE floor, uses DOWN+Jump, confirms farm-lane Y, then resumes normal farming. "
            "The separate wrong-floor FARM RETURN feature is not included. Built-in maps and maps.json remain unchanged."
        ),
    }
