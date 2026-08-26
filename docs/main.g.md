---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main.py`

## 🔧 Function `main`

```python
def main() -> None
```

Run the Harrix Swiss Knife application (tray icon and optional main window).

<details>
<summary>Code:</summary>

```python
def main() -> None:
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
```

</details>
