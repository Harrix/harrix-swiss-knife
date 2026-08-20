"""Windows uninstall launcher (`pythonw.exe launch_uninstall.py`).

Adds `src/` to `sys.path`, then opens the uninstall wizard. Catches import-time
failures so `pythonw` does not exit silently.

"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _fail(exc: BaseException) -> int:
    import os  # noqa: PLC0415

    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print(tb, file=sys.stderr, end="")
    log_path = _ROOT / "logs" / "uninstall-crash.log"
    candidates = [
        _ROOT / "logs",
        Path(os.environ["LOCALAPPDATA"]) / "harrix-swiss-knife" / "logs" if os.environ.get("LOCALAPPDATA") else None,
        Path.home() / ".harrix-swiss-knife" / "logs",
    ]
    for folder in candidates:
        if folder is None:
            continue
        try:
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / "uninstall-crash.log"
            path.write_text(tb, encoding="utf-8")
            log_path = path
            break
        except OSError:
            continue
    message = f"Harrix Swiss Knife uninstall failed to start.\n\n{exc}\n\nLog: {log_path}"
    if sys.platform == "win32":
        try:
            import ctypes  # noqa: PLC0415

            ctypes.windll.user32.MessageBoxW(None, message[:1024], "Harrix Swiss Knife", 0x10)
        except Exception:
            print("Could not show native error dialog.", file=sys.stderr)
    return 1


def main() -> int:
    """Open the uninstall wizard; return a process exit code."""
    try:
        from harrix_swiss_knife.installer.wizard import run_uninstall_wizard  # noqa: PLC0415

        return int(run_uninstall_wizard([str(_ROOT)]))
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1
    except Exception as exc:
        return _fail(exc)


if __name__ == "__main__":
    raise SystemExit(main())
