from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile


REQUIRED = [
    "NghiaClientApp.exe",
    "nghia_spotify_nologin.py",
    "maple_nghia_pro.py",
    "spotify_recovered_core.py",
    "spotify_behavior_engine.py",
    "spotify_miumiu_sell.py",
    "spotify_pc_alarm.py",
]


def test_v1011_update_zip_matches_launcher_release_contract():
    build_input = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        payload = root / "portable" / "app_payload"
        payload.mkdir(parents=True)
        for name in REQUIRED:
            (payload / name).write_bytes(b"test")

        env = os.environ.copy()
        env["PYTHONPATH"] = str(build_input)
        subprocess.run(
            [sys.executable, str(build_input / "v1011_package.py")],
            cwd=root,
            env=env,
            check=True,
        )

        update_zip = root / "out" / "NghiaEdition_Update_v10.0.11.zip"
        assert update_zip.exists()
        with ZipFile(update_zip) as zf:
            names = set(zf.namelist())
            assert "release.json" in names, (
                "launcher contract requires root release.json; without it the launcher "
                "rejects staging before payload swap/restart"
            )
            release = json.loads(zf.read("release.json").decode("utf-8"))
            assert release["version"] == "10.0.11"
            assert release["payload_dir"] == "app_payload"
            assert release["required_files"] == REQUIRED
            for name in REQUIRED:
                assert f"app_payload/{name}" in names
