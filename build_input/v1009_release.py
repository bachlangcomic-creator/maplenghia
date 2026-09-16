from __future__ import annotations

VERSION = "10.0.9"
OLD_VERSION = "10.0.8"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_MiuMiuTimer_CaptchaClientCapture_Windows.zip"


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
            "V10.0.9 exposes the existing Spotify MiuMiu sell timer in the Compact UI "
            "and makes the CAPTCHA watchdog capture Maple's exact 1280x720 client area. "
            "Adaptive Y, Anti-Jitter, STOP Non-Blocking, Loot, combat timing and maps are preserved."
        ),
    }
