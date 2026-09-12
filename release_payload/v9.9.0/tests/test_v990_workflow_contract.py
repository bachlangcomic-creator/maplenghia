from pathlib import Path

ROOT=Path(__file__).resolve().parents[3] if 'release_payload' in str(Path(__file__).resolve()) else Path('/nonexistent')
# In the repository this test lives at release_payload/v9.9.0/tests/.
def workflow_path():
    here=Path(__file__).resolve()
    repo=here.parents[3]
    return repo/'.github'/'workflows'/'publish-v9.9.0.yml'

def test_private_preflight_rebuilds_app_and_never_publishes_on_push():
    path=workflow_path()
    if not path.exists():
        # Local development layout keeps the workflow next to the overlay fixture.
        path=Path(__file__).resolve().parents[1]/'.github'/'workflows'/'publish-v9.9.0.yml'
    text=path.read_text(encoding='utf-8')
    assert 'python -m nuitka' in text
    assert 'Copy-Item dist_nuitka/NghiaClientApp.exe NghiaClientApp.exe -Force' in text
    assert 'V990_REAL_DEFAULT_LAUNCH_OK' in text
    assert 'actions/upload-artifact@v4' in text
    assert 'contents: read' in text
    assert "throw 'Public V9.9.0 publishing is intentionally locked" in text
    assert 'gh release create v9.9.0' not in text
    assert 'latest.json' not in text

def test_preflight_packages_and_reopens_update_zip():
    path=workflow_path()
    if not path.exists():
        path=Path(__file__).resolve().parents[1]/'.github'/'workflows'/'publish-v9.9.0.yml'
    text=path.read_text(encoding='utf-8')
    assert "with ZipFile(update_zip) as z:" in text
    assert "if any(n.startswith('user_data/')" in text
    assert "all_cure_workflow_evidence_ready" in text
    assert 'preflight_report.json' in text

def test_only_exact_v98_superseded_nodes_are_deselected():
    path=workflow_path()
    if not path.exists():
        path=Path(__file__).resolve().parents[1]/'.github'/'workflows'/'publish-v9.9.0.yml'
    text=path.read_text(encoding='utf-8')
    deselects=[line.strip() for line in text.splitlines() if '--deselect=' in line]
    assert len(deselects)==3
    assert any('test_scan_bridge_uses_v98_exact_asset_detector_helpers' in x for x in deselects)
    assert any('test_sell_delay_preserves_config_when_exact_bounds_unknown' in x for x in deselects)
    assert any('test_watchdog_owns_timer_state_without_random_uniform' in x for x in deselects)