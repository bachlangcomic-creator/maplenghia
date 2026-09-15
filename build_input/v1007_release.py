from __future__ import annotations

VERSION = "10.0.7"
OLD_VERSION = "10.0.6"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_AntiJitter_Hysteresis_Windows.zip"


def bump_ui_text(text: str) -> str:
    if OLD_VERSION not in text:
        raise ValueError(f"expected source to contain {OLD_VERSION}")
    bumped = text.replace(OLD_VERSION, VERSION)
    if OLD_VERSION in bumped:
        raise ValueError(f"failed to replace all {OLD_VERSION} occurrences")
    return bumped


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
            "V10.0.7 Anti-Jitter / Hysteresis stable. Same validated farm/runtime "
            "behavior as the V10.0.6 Anti-Jitter candidate, promoted to a new semantic "
            "version so existing V10.0.6 clients receive the update."
        ),
    }
