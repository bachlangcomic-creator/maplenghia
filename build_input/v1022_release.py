from __future__ import annotations
VERSION = "10.0.22"
OLD_VERSION = "10.0.21"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_TwoFloorSafeUI_Windows.zip"

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
            "V10.0.22 cleans up TWO FLOOR ROUTE setup: the top FARM/SAFE section shows only SAFE ENTRY and SAFE, "
            "while farming coordinates come exclusively from BOTTOM/TOP LEFT-RIGHT plus UP/DOWN POINT. "
            "TWO FLOOR also exposes SIMPLE Human Behavior, B1/B3 Fall Recovery, and Spotify Loot Jitter; "
            "the dedicated Two Floor Recovery remains separate. V10.0.21 pass count, V10.0.20 Edit Map, "
            "V10.0.19 CAPTCHA Scale Latch, and V10.0.18 MiuMiu Strict are preserved."
        ),
    }
