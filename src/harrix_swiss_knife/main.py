"""Main module for Harrix Swiss Knife application.

This module contains the main application logic for the Harrix Swiss Knife tool,
including the menu structure and application initialization.

"""

from __future__ import annotations

import logging
import sys
import traceback
from pathlib import Path

# Desktop / Startup shortcuts launch `pythonw.exe …/src/harrix_swiss_knife/main.py`.
# That puts the package directory on `sys.path`, not `src/`, so without an editable
# venv install the package is invisible until `src/` is added here.
_SRC_ROOT = Path(__file__).resolve().parent.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


def _report_bootstrap_failure(exc: BaseException) -> None:
    """Show and log failures that happen before Qt logging is ready (e.g. under pythonw)."""
    import os  # noqa: PLC0415

    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print(tb, file=sys.stderr, end="")
    log_path = Path("startup-crash.log")
    candidates = [_SRC_ROOT.parent / "logs"]
    appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "harrix-swiss-knife" / "logs")
    candidates.append(Path.home() / ".harrix-swiss-knife" / "logs")
    for folder in candidates:
        try:
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / "startup-crash.log"
            path.write_text(tb, encoding="utf-8")
            log_path = path
            break
        except OSError:
            continue
    message = f"Harrix Swiss Knife failed to start.\n\n{exc}\n\nLog: {log_path}"
    if sys.platform == "win32":
        try:
            import ctypes  # noqa: PLC0415

            ctypes.windll.user32.MessageBoxW(None, message[:1024], "Harrix Swiss Knife", 0x10)
        except Exception:
            logging.getLogger(__name__).debug("Native error dialog failed", exc_info=True)


def main() -> None:
    """Run the Harrix Swiss Knife application (tray icon and optional main window)."""
    from harrix_swiss_knife.early_splash import close_early_splash, ensure_early_splash  # noqa: PLC0415

    ensure_early_splash()

    from harrix_swiss_knife.uv_locate import refresh_path  # noqa: PLC0415

    # Desktop shortcuts often inherit Explorer's PATH from before the installer
    # added `%USERPROFILE%\\.local\\bin` (uv / hsk). Refresh before any actions.
    refresh_path()

    from harrix_swiss_knife.app_startup import (  # noqa: PLC0415
        install_diagnostic_handlers,
        log_startup_context,
        run_tray_application,
        setup_file_logging,
        show_fatal_error_dialog,
    )
    from harrix_swiss_knife.main_menu_base import MainMenuBase  # noqa: PLC0415
    from harrix_swiss_knife.menu_structure import get_menu_structure  # noqa: PLC0415

    class MainMenu(MainMenuBase):
        """Main menu class that defines the application's menu structure."""

        def __init__(self, *, output_bus: object, config: dict | None = None) -> None:
            """Create all menu categories and their items."""
            super().__init__(output_bus=output_bus, config=config)
            self.add_menu_structure(self.menu, get_menu_structure())

    log_path = setup_file_logging()
    log = logging.getLogger("harrix_swiss_knife")
    install_diagnostic_handlers(log)
    log_startup_context(log, log_path)

    try:
        rc = run_tray_application(log, main_menu_cls=MainMenu)
        sys.exit(rc)
    except SystemExit:
        raise
    except Exception:
        close_early_splash()
        tb = traceback.format_exc()
        log.exception("Fatal error during startup; exiting.")
        show_fatal_error_dialog(f"Fatal error during startup.\n\nLog: {log_path}\n\n{tb}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        _report_bootstrap_failure(exc)
        raise SystemExit(1) from exc
