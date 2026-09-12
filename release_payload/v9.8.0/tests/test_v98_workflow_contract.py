from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WF = ROOT / '.github' / 'workflows' / 'publish-v9.8.0.yml'


def workflow_text():
    assert WF.exists(), 'publish-v9.8.0.yml is missing'
    return WF.read_text(encoding='utf-8')


def test_v98_workflow_uses_exact_public_v97_base_and_normalizes_after_hash_gate():
    text = workflow_text()
    assert 'NghiaClient_V9.7.0_Portable.zip' in text
    assert '09f70ba29b5a55aa84c040c195d3ab629259214f3c745105e691678d225b0086' in text
    for sha in (
        'aa1b14d74b6bbacd91d6c8dc18ebb8fdc462b3df345ded5a9338b47f7601433d',
        '5f3ba4dfa9886d75b80d39aca29e79ab500435e25e8dc592bc9423050d15675d',
        '4ed97d1eb1ff2ef3758fc243da600155fada71701f24b63b832fdc675cf84f08',
    ):
        assert sha in text
    assert "replace(b'\\r\\n', b'\\n')" in text
    assert text.index('V970_PROTECTED_BASE_HASHES_OK') < text.index("replace(b'\\r\\n', b'\\n')")


def test_v98_workflow_packages_modules_evidence_and_keeps_publish_hard_gated():
    text = workflow_text()
    for name in (
        'spotify_exact_assets.py', 'spotify_detection_parity.py',
        'spotify_watchdog.py', 'spotify_all_cure_market.py',
        'evidence/all_cure_market.json', 'evidence/revive_action.json',
        'evidence/dynamic_combo_callers.json', 'evidence/main_farm_worker.json',
    ):
        assert name in text
    assert 'publish:' in text and 'default: false' in text
    assert 'if: ${{ inputs.publish }}' in text
    assert 'V980_PYTEST_OK' in text
    assert 'V980_REAL_DEFAULT_LAUNCH_OK' in text
    assert 'V980_PACKAGE_OK' in text
    assert 'PUBLIC_V980_ASSET_HASHES_OK' in text
    assert 'LATEST_JSON_PUBLISHED' in text
