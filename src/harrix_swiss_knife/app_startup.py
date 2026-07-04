"""File logging, fatal-error UI, and tray application bootstrap."""

from __future__ import annotations

import faulthandler
import logging
import os
import sys
import threading
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING

import harrix_pylib as h
from PySide6.QtCore import QtMsgType, qInstallMessageHandler
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

import harrix_swiss_knife as hsk
from harrix_swiss_knife import main_window, resources_rc  # noqa: F401
from harrix_swiss_knife.action_output_bus import ActionOutputBus
from harrix_swiss_knife.global_hotkey import GlobalHotkeyManager
from harrix_swiss_knife.menu_structure import get_menu_structure
from harrix_swiss_knife.paths import get_config_path_str, prune_action_output_dir
from harrix_swiss_knife.quick_launcher_context import QuickLauncherContext, set_quick_launcher_context
from harrix_swiss_knife.quick_launcher_hotkey import load_quick_launcher_hotkey

if TYPE_CHECKING:
    from types import TracebackType

    from harrix_swiss_knife.main_menu_base import MainMenuBase


def get_log_dir() -> Path:
    """Pick a writable log directory: <repo>/logs first, then %LOCALAPPDATA%/harrix-swiss-knife/logs."""
    here = Path(__file__).resolve().parent  # src/harrix_swiss_knife
    project_root = here.parent.parent
    candidates = [project_root / "logs"]
    appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "harrix-swiss-knife" / "logs")
    candidates.append(Path.home() / ".harrix-swiss-knife" / "logs")
    for c in candidates:
        try:
            c.mkdir(parents=True, exist_ok=True)
            test = c / ".write-test"
            test.write_text("ok", encoding="utf-8")
            test.unlink(missing_ok=True)
        except Exception:
            logging.getLogger(__name__).debug("Log dir candidate is not writable: %s", c, exc_info=True)
        else:
            return c
    return Path.cwd()


def install_diagnostic_handlers(log: logging.Logger) -> None:
    """Route uncaught errors, thread failures, segfaults, and Qt messages to stderr and log.

    Console (stderr) receives only WARNING and above; full INFO logs stay in the file handler.
    """
    root = logging.getLogger()
    stderr_handler: logging.StreamHandler | None = None
    for h_ in root.handlers:
        if isinstance(h_, logging.StreamHandler) and h_.stream is sys.stderr:
            stderr_handler = h_
            break
    if stderr_handler is None:
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        root.addHandler(stderr_handler)
    stderr_handler.setLevel(logging.WARNING)

    def _excepthook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> None:
        tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(tb_text, file=sys.stderr, end="")
        log.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

    sys.excepthook = _excepthook

    if hasattr(threading, "excepthook"):

        def _thread_excepthook(args: threading.ExceptHookArgs) -> None:
            tb_text = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
            print(tb_text, file=sys.stderr, end="")
            thread_name = getattr(args.thread, "name", args.thread)
            if args.exc_value is None:
                log.error("Uncaught exception in thread %s", thread_name)
            else:
                log.error(
                    "Uncaught exception in thread %s",
                    thread_name,
                    exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
                )

        threading.excepthook = _thread_excepthook

    faulthandler.enable(file=sys.stderr, all_threads=True)

    _qt_msg_levels = {
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }

    def _qt_message_handler(msg_type: QtMsgType, context: object, message: str) -> None:
        if msg_type not in _qt_msg_levels:
            return
        level = _qt_msg_levels[msg_type]
        location = ""
        if context is not None and hasattr(context, "file") and hasattr(context, "line"):
            location = f" ({context.file}:{context.line})"
        text = f"Qt: {message}{location}"
        print(text, file=sys.stderr)
        log.log(level, text)

    qInstallMessageHandler(_qt_message_handler)


def log_startup_context(log: logging.Logger, log_path: Path) -> None:
    """Write one-shot startup diagnostics (Python version, argv, CWD, log path)."""
    log.info("=" * 60)
    log.info("Starting Harrix Swiss Knife")
    log.info("Log file: %s", log_path)
    log.info("Python: %s", sys.version.replace("\n", " "))
    log.info("Platform: %s", sys.platform)
    log.info("Executable: %s", sys.executable)
    log.info("Argv: %s", sys.argv)
    log.info("CWD: %s", Path.cwd())


def run_tray_application(log: logging.Logger, *, main_menu_cls: type[MainMenuBase]) -> int:
    """Create QApplication, tray, main window, and run until the event loop exits."""
    prune_action_output_dir()
    log.info("Creating QApplication")
    app: QApplication = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    output_bus = ActionOutputBus()
    log.info("Building main menu")
    main_menu = main_menu_cls(output_bus=output_bus)
    log.info("Creating tray icon")
    tray_icon: hsk.tray_icon.TrayIcon = hsk.tray_icon.TrayIcon(
        QIcon(":/assets/logo.svg"), menu=main_menu.menu, output_bus=output_bus
    )
    tray_icon.setToolTip("Harrix Swiss Knife")
    tray_icon.show()

    if not tray_icon.isSystemTrayAvailable():
        log.warning("System tray is not available on this system; tray icon will not be visible.")
    if not tray_icon.isVisible():
        log.warning("Tray icon failed to become visible. Windows may hide tray icons by default.")

    config: dict = h.dev.config_load(get_config_path_str())
    show_main_window: bool = config.get("show_main_window_on_startup", True)

    log.info("Creating main window (show_on_startup=%s)", show_main_window)
    main_window_instance: main_window.MainWindow = main_window.MainWindow(main_menu.menu, output_bus=output_bus)
    tray_icon.main_window = main_window_instance

    if show_main_window:
        main_window_instance.show_window()

    hotkey_manager = GlobalHotkeyManager(app) if sys.platform == "win32" else None
    if hotkey_manager is not None:
        saved_hotkey = load_quick_launcher_hotkey()
        if saved_hotkey:
            hotkey_manager.register(saved_hotkey)
        hotkey_manager.registration_failed.connect(lambda msg: log.warning("Quick launcher hotkey: %s", msg))

    context = QuickLauncherContext(
        output_bus=output_bus,
        hotkey_manager=hotkey_manager,
        menu_structure_provider=get_menu_structure,
        parent=main_window_instance,
    )
    set_quick_launcher_context(context)

    if hotkey_manager is not None:
        hotkey_manager.hotkey_triggered.connect(context.toggle)

    log.info("Entering Qt event loop")
    rc = app.exec()
    log.info("Qt event loop exited with code %s", rc)
    return rc


def setup_file_logging() -> Path:
    """Add a rotating file handler so we can diagnose tray-not-appearing issues."""
    log_dir = get_log_dir()
    log_path = log_dir / "main.log"
    root = logging.getLogger()
    if not any(isinstance(h_, RotatingFileHandler) for h_ in root.handlers):
        fh = RotatingFileHandler(str(log_path), maxBytes=2_000_000, backupCount=3, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        root.addHandler(fh)
    if root.level == logging.NOTSET or root.level > logging.INFO:
        root.setLevel(logging.INFO)
    return log_path


def show_fatal_error_dialog(text: str) -> None:
    """Try to show a Qt error dialog when the app fails before reaching the tray."""
    try:
        if QApplication.instance() is None:
            QApplication(sys.argv)
        QMessageBox.critical(None, "Harrix Swiss Knife - Error", text)
    except Exception:
        logging.getLogger(__name__).debug("Failed to show Qt error dialog.", exc_info=True)
