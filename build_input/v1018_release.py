from __future__ import annotations

VERSION = "10.0.18"
OLD_VERSION = "10.0.17"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_MiuMiuStrict_Windows.zip"

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
            "V10.0.18 keeps V10.0.17 Custom SAFE ENTRY + Return To Farm and hardens MiuMiu selling: "
            "only MiuMiu uses verified double-left-click (80-120 ms inter-click, 10-30 ms hold); all other UI actions remain single-click. "
            "Shop opening is verified with MIUMIU_OPENED_B64 and retried at most once. Equip then ETC selling now requires strict Confirm appearance/click/disappearance, "
            "ETC failures propagate to the whole sale, and false-success paths are removed."
        ),
    }
