from __future__ import annotations

VERSION = "10.0.15"
OLD_VERSION = "10.0.14"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_HumanRestMs_Windows.zip"


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
            "V10.0.15 keeps SIMPLE Human Behavior at 2% rest, 6% jump, 92% continue, "
            "but shortens the rest window from 3-5 seconds to 1000-1500 ms. "
            "Jump remains 150-300 ms. V10.0.14 Sell Trigger Arbitration and V10.0.13 Custom Map Sell-Safe are preserved."
        ),
    }
