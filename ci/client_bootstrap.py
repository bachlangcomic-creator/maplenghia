from pathlib import Path
import runpy
import sys


def main() -> None:
    app_dir = Path(sys.argv[0]).resolve().parent
    target = app_dir / "nghia_spotify_nologin.py"
    if not target.is_file():
        raise SystemExit(f"Missing app entrypoint: {target}")
    sys.path.insert(0, str(app_dir))
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
