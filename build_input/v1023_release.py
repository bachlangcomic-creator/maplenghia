from __future__ import annotations
VERSION = "10.0.23"
OLD_VERSION = "10.0.22"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_TwoFloorNatural_Windows.zip"

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
            "V10.0.23 restores the natural V10.0.18-style run/attack cadence while TWO FLOOR travels horizontally "
            "toward UP_POINT or DOWN_POINT. Transition travel no longer consumes every combat tick; the movement "
            "direction is synchronized to the target, while vertical mismatch and WAIT_TOP/WAIT_BOTTOM remain safety-gated. "
            "V10.0.22 SAFE UI, V10.0.21 pass count, V10.0.20 Edit Map, V10.0.19 CAPTCHA Scale Latch, and V10.0.18 MiuMiu Strict are preserved."
        ),
    }
