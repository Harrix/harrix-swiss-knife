---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `app_startup.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_log_dir`](#-function-get_log_dir)
- [🔧 Function `install_diagnostic_handlers`](#-function-install_diagnostic_handlers)
- [🔧 Function `is_ignored_qt_message`](#-function-is_ignored_qt_message)
- [🔧 Function `log_startup_context`](#-function-log_startup_context)
- [🔧 Function `run_tray_application`](#-function-run_tray_application)
- [🔧 Function `setup_file_logging`](#-function-setup_file_logging)
- [🔧 Function `show_fatal_error_dialog`](#-function-show_fatal_error_dialog)

</details>

## 🔧 Function `get_log_dir`

```python
def get_log_dir() -> Path
```

Pick a writable log directory: <repo>/logs first, then %LOCALAPPDATA%/harrix-swiss-knife/logs.

<details>
<summary>Code:</summary>

```python
def get_log_dir() -> Path:
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
```

</details>

## 🔧 Function `install_diagnostic_handlers`

```python
def install_diagnostic_handlers(log: logging.Logger) -> None
```

Route uncaught errors, thread failures, segfaults, and Qt messages to stderr and log.

Console (stderr) receives only WARNING and above; full INFO logs stay in the file handler.
Shortcuts run the app through `pythonw.exe` (or the GUI script wrapper), where
`sys.stderr` is `None`, so every console hookup here stays optional.

<details>
<summary>Code:</summary>

```python
def install_diagnostic_handlers(log: logging.Logger) -> None:
    stderr = _usable_stderr()
    root = logging.getLogger()
    if stderr is not None:
        stderr_handler: logging.Handler | None = None
        for h_ in root.handlers:
            if isinstance(h_, logging.StreamHandler) and h_.stream is stderr:
                stderr_handler = h_
                break
        if stderr_handler is None:
            stream_handler = logging.StreamHandler(stderr)
            stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
            root.addHandler(stream_handler)
            stderr_handler = stream_handler
        stderr_handler.setLevel(logging.WARNING)

    def _excepthook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> None:
        tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(tb_text, file=sys.stderr, end="")
        log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

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

    _enable_faulthandler(log)

    _qt_msg_levels = {
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }

    def _qt_message_handler(msg_type: QtMsgType, context: object, message: str) -> None:
        if msg_type not in _qt_msg_levels:
            return
        if is_ignored_qt_message(message):
            return
        level = _qt_msg_levels[msg_type]
        location = ""
        if context is not None and hasattr(context, "file") and hasattr(context, "line"):
            location = f" ({context.file}:{context.line})"
        text = f"Qt: {message}{location}"
        print(text, file=sys.stderr)
        log.log(level, text)

    qInstallMessageHandler(_qt_message_handler)
```

</details>

## 🔧 Function `is_ignored_qt_message`

```python
def is_ignored_qt_message(message: str) -> bool
```

Return whether a Qt message is known harmless renderer or display noise.

<details>
<summary>Code:</summary>

```python
def is_ignored_qt_message(message: str) -> bool:
    return any(part in message for part in _QT_IGNORED_SUBSTRINGS)
```

</details>

## 🔧 Function `log_startup_context`

```python
def log_startup_context(log: logging.Logger, log_path: Path) -> None
```

Write one-shot startup diagnostics (Python version, argv, CWD, log path).

<details>
<summary>Code:</summary>

```python
def log_startup_context(log: logging.Logger, log_path: Path) -> None:
    log.info("=" * 60)
    log.info("Starting Harrix Swiss Knife")
    log.info("Log file: %s", log_path)
    log.info("Python: %s", sys.version.replace("\n", " "))
    log.info("Platform: %s", sys.platform)
    log.info("Executable: %s", sys.executable)
    log.info("Argv: %s", sys.argv)
    log.info("CWD: %s", Path.cwd())
```

</details>

## 🔧 Function `run_tray_application`

```python
def run_tray_application(log: logging.Logger, *, main_menu_cls: type[MainMenuBase]) -> int
```

Create QApplication, tray, main window, and run until the event loop exits.

<details>
<summary>Code:</summary>

```python
def run_tray_application(log: logging.Logger, *, main_menu_cls: type[MainMenuBase]) -> int:
    startup_t0 = perf_counter()
    config: dict = h.dev.config_load(get_config_path_str())

    _log_startup_phase(log, "Creating QApplication", startup_t0)
    existing = QApplication.instance()
    app = cast("QApplication", existing) if existing is not None else QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))
    install_flexible_decimal_separators(app)
    install_app_fonts(app)
    install_safe_qt_translate()
    if early_splash_hwnd():
        _log_startup_phase(log, "Startup splash already visible", startup_t0)

    tray_ready = False
    pending_show = False
    tray_icon_holder: TrayIcon | None = None

    def show_command_cards() -> None:
        nonlocal pending_show
        if tray_icon_holder is None or not tray_ready:
            pending_show = True
            return
        tray_icon_holder.show_command_window()

    if acquire_tray_instance(show_command_cards) is None:
        log.info("Another instance is already running; asked it to show the command window")
        close_early_splash()
        return 0

    output_bus = ActionOutputBus()
    placeholder_menu = _make_placeholder_menu()

    _log_startup_phase(log, "Creating tray icon", startup_t0)
    tray_icon = TrayIcon(QIcon(":/assets/logo.svg"), menu=placeholder_menu)
    tray_icon_holder = tray_icon
    tray_icon.setToolTip("Harrix Swiss Knife")
    tray_icon.show()
    _log_startup_phase(log, "Tray visible", startup_t0)

    if not tray_icon.isSystemTrayAvailable():
        log.warning("System tray is not available on this system; tray icon will not be visible.")
    if not tray_icon.isVisible():
        log.warning("Tray icon failed to become visible. Windows may hide tray icons by default.")

    show_main_window = get_show_main_window_on_startup(config)

    def finish_startup() -> None:
        nonlocal tray_ready
        try:
            _log_startup_phase(log, "Building main menu", startup_t0)
            main_menu = main_menu_cls(output_bus=output_bus, config=config)
            set_menu_tooltips_visible_recursive(main_menu.menu)
            tray_icon.setContextMenu(main_menu.menu)
            tray_icon.menu = main_menu.menu
            _log_startup_phase(log, "Main menu ready", startup_t0)
            tray_ready = True
        finally:
            close_early_splash()

        if show_main_window or pending_show:
            log.info("Showing main window on startup")
            tray_icon.show_command_window()

        _offer_data_for_hsk_setup_if_needed(config, log)

    def _offer_data_for_hsk_setup_if_needed(cfg: dict, startup_log: logging.Logger) -> None:
        created = ensure_missing_tracker_databases(cfg)
        if created:
            startup_log.info("Created missing tracker database(s): %s", ", ".join(created))
        if not needs_data_for_hsk_setup(cfg):
            return
        reply = QMessageBox.question(
            None,
            "Set up personal data folder?",
            (
                "Harrix Swiss Knife can create a `data-for-hsk` folder with SQLite databases "
                "and Notes subfolders outside the application directory.\n\n"
                "Recommended before using Finance, Food, Fitness, Habits, Quick paste, "
                "and note actions.\n\n"
                "You can also run Dev → Set up data-for-hsk later."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            startup_log.info("User skipped data-for-hsk setup on first run")
            return
        run_setup_data_for_hsk_dialog(cfg, parent=None, log=startup_log)

    QTimer.singleShot(0, finish_startup)
    QTimer.singleShot(0, prune_action_output_dir)

    context = QuickLauncherContext(
        output_bus=output_bus,
        menu_structure_provider=get_menu_structure,
        parent=None,
    )
    set_quick_launcher_context(context)

    hotkey_manager = GlobalHotkeyManager(app) if sys.platform == "win32" else None
    if hotkey_manager is not None:
        action_by_name = {cls.__name__: cls for cls in iter_menu_structure(get_menu_structure())}

        def run_hotkey_action(action_name: str) -> None:
            action_cls = action_by_name.get(action_name)
            if action_cls is None:
                log.warning("Hotkey bound to unknown action %r", action_name)
                return
            try:
                action_cls(parent=None, output_bus=output_bus)()
            except Exception:
                log.exception("Hotkey action %s failed", action_name)

        bindings = load_action_hotkeys(config)
        hotkey_manager.registration_failed.connect(lambda msg: log.warning("Global hotkey: %s", msg))
        registered = hotkey_manager.register_all(bindings)
        log.info("Registered %s global hotkey(s) from config.json", registered)
        hotkey_manager.action_triggered.connect(run_hotkey_action)

    _log_startup_phase(log, "Entering Qt event loop", startup_t0)
    rc = app.exec()
    log.info("Qt event loop exited with code %s", rc)
    return rc
```

</details>

## 🔧 Function `setup_file_logging`

```python
def setup_file_logging() -> Path
```

Add a rotating file handler so we can diagnose tray-not-appearing issues.

<details>
<summary>Code:</summary>

```python
def setup_file_logging() -> Path:
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
```

</details>

## 🔧 Function `show_fatal_error_dialog`

```python
def show_fatal_error_dialog(text: str) -> None
```

Try to show a Qt error dialog when the app fails before reaching the tray.

<details>
<summary>Code:</summary>

```python
def show_fatal_error_dialog(text: str) -> None:
    try:
        if QApplication.instance() is None:
            QApplication(sys.argv)
        QMessageBox.critical(None, "Harrix Swiss Knife - Error", text)
    except Exception:
        logging.getLogger(__name__).debug("Failed to show Qt error dialog.", exc_info=True)
```

</details>
