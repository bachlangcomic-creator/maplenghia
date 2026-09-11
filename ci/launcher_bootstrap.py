from pathlib import Path
import sys


def main() -> int:
    root = Path(sys.argv[0]).resolve().parent
    target = root / "launcher" / "nghia_launcher.py"
    if not target.is_file():
        raise SystemExit(f"Missing launcher entrypoint: {target}")
    sys.path.insert(0, str(root))
    from launcher.nghia_launcher import main as launcher_main
    return int(launcher_main())


if __name__ == "__main__":
    raise SystemExit(main())
