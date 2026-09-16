from __future__ import annotations

VERSION = "10.0.12"
OLD_VERSION = "10.0.11"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_WatchdogPreviewTypeFix_Windows.zip"


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
            "V10.0.12 fixes the watchdog annotated-preview crash where SpotifyDetectionResult "
            "objects could be cached and later unpacked as drawable (score, x, y, w, h) boxes. "
            "V10.0.11 Custom Map, MiuMiu, Adaptive Y, Anti-Jitter, STOP and core behavior are preserved."
        ),
    }
