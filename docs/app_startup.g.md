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
def run_tray_application(log: logging.Logger) -> int
```

Create QApplication, tray, main window, and run until the event loop exits.

<details>
<summary>Code:</summary>

```python
def run_tray_application(log: logging.Logger, *, main_menu_cls: type[MainMenuBase]) -> int:
    prune_action_output_dir()
    log.info("Creating QApplication")
    app: QApplication = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    output_bus = ActionOutputBus()
    log.info("Building main menu")
    main_menu = main_menu_cls(output_bus=output_bus)
    log.info("Creating tray icon")
    tray_icon: hsk.tray_icon.TrayIcon = hsk.tray_icon.TrayIcon(QIcon(":/assets/logo.svg"), menu=main_menu.menu)
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

    log.info("Entering Qt event loop")
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
