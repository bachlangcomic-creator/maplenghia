from __future__ import annotations
VERSION='10.0.16'
OLD_VERSION='10.0.15'
TAG=f'v{VERSION}'
UPDATE_ASSET=f'NghiaEdition_Update_v{VERSION}.zip'
PORTABLE_ASSET=f'NghiaClient_V{VERSION}_CustomSafeReturn_Windows.zip'

def stable_manifest(sha256: str) -> dict[str,str]:
    package_url=(
        'https://github.com/bachlangcomic-creator/maplenghia/releases/'
        f'download/{TAG}/{UPDATE_ASSET}'
    )
    return {
        'version':VERSION,
        'channel':'stable',
        'package_url':package_url,
        'url':package_url,
        'sha256':sha256,
        'payload_dir':'app_payload',
        'min_launcher_version':'1.0.1',
        'notes':(
            'V10.0.16 adds Custom Map SAFE ENTRY and FARM RETURN on top of V10.0.15. '
            'SAFE ENTRY routes to the climb point, performs UP + Jump, then verifies SAFE before MiuMiu. '
            'FARM RETURN routes back to the drop point and performs DOWN + Jump before farming resumes. '
            'The feature is isolated to V10 Custom Map profiles; bundled/original map profiles and protected Spotify core files remain unchanged.'
        ),
    }
