import sys
from pathlib import Path

APP = Path('portable/app_payload').resolve()
sys.path.insert(0, str(APP))

import korean_question_helper as kqh


def test_find_tesseract_beside_compiled_executable(tmp_path, monkeypatch):
    """Nuitka onefile must locate OCR beside the real exe, not __file__."""
    app_dir = tmp_path / 'app_payload'
    app_dir.mkdir()
    exe = app_dir / 'NghiaClientApp.exe'
    exe.write_bytes(b'MZ')
    tess = app_dir / 'tesseract' / 'tesseract.exe'
    tess.parent.mkdir()
    tess.write_bytes(b'MZ')

    monkeypatch.delenv('TESSERACT_CMD', raising=False)
    monkeypatch.setenv('PATH', '')
    monkeypatch.setattr(sys, 'argv', [str(exe)])

    assert kqh._find_tesseract_cmd() == str(tess)
