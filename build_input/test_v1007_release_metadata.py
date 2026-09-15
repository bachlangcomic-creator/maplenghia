import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_release_module():
    path = ROOT / "v1007_release.py"
    assert path.is_file(), "v1007 release helper is missing"
    spec = importlib.util.spec_from_file_location("v1007_release", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_bump_ui_text_rewrites_semantic_version_only():
    mod = load_release_module()
    src = (
        'title = "Nghia Edition V10.0.6"\n'
        'local = os.environ.get("NGHIA_LOCAL_VERSION", "10.0.6")\n'
        'label = "Anti-Jitter / Hysteresis • OFF = V10.0.6 gốc"\n'
    )
    out = mod.bump_ui_text(src)
    assert "10.0.6" not in out
    assert out.count("10.0.7") == 3


def test_bump_ui_text_refuses_unexpected_source():
    mod = load_release_module()
    try:
        mod.bump_ui_text('title = "already new"\n')
    except ValueError as exc:
        assert "10.0.6" in str(exc)
    else:
        raise AssertionError("expected ValueError for source without old version")


def test_stable_manifest_points_to_v1007_asset():
    mod = load_release_module()
    manifest = mod.stable_manifest("abc123")
    assert manifest["version"] == "10.0.7"
    assert manifest["channel"] == "stable"
    assert manifest["sha256"] == "abc123"
    assert manifest["package_url"].endswith(
        "/releases/download/v10.0.7/NghiaEdition_Update_v10.0.7.zip"
    )
    assert manifest["url"] == manifest["package_url"]
    assert manifest["payload_dir"] == "app_payload"
    assert manifest["min_launcher_version"] == "1.0.1"
