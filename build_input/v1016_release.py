from __future__ import annotations

VERSION = "10.0.16"
OLD_VERSION = "10.0.15"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_CustomSafeEntryReturnToFarm_Windows.zip"


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
            "V10.0.16 adds optional Custom Map SAFE ENTRY for MiuMiu: move to SAFE ENTRY, perform UP + configured Jump, "
            "then move/verify SAFE before selling. After a successful sale, RETURN TO FARM reuses SAFE ENTRY X: align horizontally "
            "on the SAFE floor, perform DOWN + configured Jump, confirm farm-lane Y, then resume LEFT/RIGHT farming. "
            "Custom Maps without SAFE ENTRY keep the previous direct-SAFE behavior. The separate FARM RETURN wrong-floor recovery feature "
            "is intentionally deferred. Original bundled maps and protected Spotify/core behavior remain unchanged."
        ),
    }
