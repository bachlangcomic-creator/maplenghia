from __future__ import annotations

VERSION = "10.0.8"
OLD_VERSION = "10.0.7"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_AdaptiveY_MapAware_Windows.zip"


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
            "V10.0.8 adds a visible map-aware Adaptive Y ON/OFF control for C2/B3. "
            "C2 and B3 keep their existing Adaptive Y engines; other maps disable the control. "
            "Anti-Jitter, STOP Non-Blocking, Loot Parity Defense, combat timing and maps are preserved."
        ),
    }
