from __future__ import annotations

VERSION = "10.0.14"
OLD_VERSION = "10.0.13"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_SellTriggerArbitration_Windows.zip"


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
            "V10.0.14 fixes MiuMiu sell-trigger arbitration. With the sell timer enabled, only the timer event may start SELL_SAFE; "
            "full-bag detections and legacy sell_only_when_full state can no longer steal movement/skill input before the timer is due. "
            "Toggling Auto Sell also clears stale sell triggers and restarts the timer schedule. V10.0.13 Custom Map Sell-Safe is preserved."
        ),
    }
