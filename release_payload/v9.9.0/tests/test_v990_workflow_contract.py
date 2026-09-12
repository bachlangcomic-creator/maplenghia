from pathlib import Path

def workflow_path():
    return Path(__file__).resolve().parents[3]/'.github'/'workflows'/'publish-v9.9.0.yml'
def test_private_preflight_rebuilds_app_and_never_publishes_on_push():
    text=workflow_path().read_text(encoding='utf-8');assert 'python -m nuitka' in text;assert 'Copy-Item dist_nuitka/NghiaClientApp.exe NghiaClientApp.exe -Force' in text;assert 'V990_REAL_DEFAULT_LAUNCH_OK' in text;assert 'actions/upload-artifact@v4' in text;assert 'contents: read' in text;assert "throw 'Public V9.9.0 publishing is intentionally locked" in text;assert 'gh release create v9.9.0' not in text;assert 'latest.json' not in text
def test_preflight_packages_and_reopens_update_zip():
    text=workflow_path().read_text(encoding='utf-8');assert 'with ZipFile(update_zip) as z:' in text;assert "if any(n.startswith('user_data/')" in text;assert 'all_cure_workflow_evidence_ready' in text;assert 'preflight_report.json' in text
