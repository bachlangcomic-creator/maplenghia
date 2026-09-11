from pathlib import Path
import runpy
import sys


def main() -> None:
    root = Path(sys.argv[0]).resolve().parent
    target = root / "launcher" / "nghia_launcher.py"
    if not target.is_file():
        raise SystemExit(f"Missing launcher entrypoint: {target}")
    sys.path.insert(0, str(root))
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
