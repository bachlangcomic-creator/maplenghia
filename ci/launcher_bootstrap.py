from pathlib import Path
import sys
import traceback


def _report_crash(root: Path, text: str) -> None:
    try:
        user_data = root / "user_data"
        user_data.mkdir(parents=True, exist_ok=True)
        (user_data / "launcher_crash.log").write_text(text, encoding="utf-8")
    except Exception:
        pass

    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                None,
                text[-3500:],
                "NghiaLauncher - Loi khoi dong",
                0x10,
            )
        except Exception:
            pass


def main() -> int:
    root = Path(sys.argv[0]).resolve().parent
    try:
        target = root / "launcher" / "nghia_launcher.py"
        if not target.is_file():
            raise FileNotFoundError(f"Missing launcher entrypoint: {target}")
        sys.path.insert(0, str(root))
        from launcher.nghia_launcher import main as launcher_main
        return int(launcher_main())
    except Exception:
        text = traceback.format_exc()
        _report_crash(root, text)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
