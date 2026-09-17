from __future__ import annotations
VERSION = "10.0.19"
OLD_VERSION = "10.0.18"
TAG = f"v{VERSION}"
UPDATE_ASSET = f"NghiaEdition_Update_v{VERSION}.zip"
PORTABLE_ASSET = f"NghiaClient_V{VERSION}_CaptchaScaleLatch_Windows.zip"

def stable_manifest(sha256: str) -> dict[str, str]:
    package_url=(
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
            "V10.0.19 keeps V10.0.18 MiuMiu Strict and improves Spotify-style CAPTCHA alerts: "
            "LIE_B64 is matched across scales 0.90/0.95/1.00/1.05/1.10 at the recovered 0.70 threshold, "
            "the alert fires once on APPEARED, and CAPTCHA pause clears only after 3 clean frames. "
            "QUESTION_CAPTCHA assets are not used as independent alarm triggers."
        ),
    }
