from __future__ import annotations

VERSION = "10.0.13"
OLD_VERSION = "10.0.12"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_CustomMapSellSafe_Windows.zip"


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
            "V10.0.13 connects Custom Map STRATEGY_V10 to the existing SELL_SAFE/MiuMiu flow. "
            "When Auto Sell and the sell timer are enabled, timer due now preempts farm, moves to the Custom Map SAFE_PLACE, "
            "runs the existing MiuMiu seller, blocks Strategy inputs while selling, then resumes farm. V10.0.12 fixes are preserved."
        ),
    }
