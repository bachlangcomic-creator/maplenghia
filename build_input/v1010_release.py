from __future__ import annotations

VERSION = "10.0.10"
OLD_VERSION = "10.0.9"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_CustomMapParity_Windows.zip"


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
            "V10.0.10 is based on V10.0.9 and adds optional Custom Map parity controls: "
            "SIMPLE Human Behavior, B1/B3-style Fall Recovery, Spotify-style Loot Jitter, "
            "and independent Custom Map Adaptive Y. All four options default OFF. "
            "V10.0.9 MiuMiu timer and CAPTCHA client-area capture are preserved."
        ),
    }
