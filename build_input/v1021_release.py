from __future__ import annotations
VERSION = "10.0.21"
OLD_VERSION = "10.0.20"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_TwoFloorPassCount_Windows.zip"

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
            "V10.0.21 adds a 1-10 'Số lượt mỗi tầng' control for TWO FLOOR ROUTE. "
            "Only a full crossing from one lane edge to the opposite edge counts as one pass; the first edge only arms the counter. "
            "The bot changes floor only after the configured pass count and still requires verified Y before accepting the new floor. "
            "V10.0.20 Edit Custom Map, V10.0.19 CAPTCHA Scale Latch, and V10.0.18 MiuMiu Strict are preserved."
        ),
    }
