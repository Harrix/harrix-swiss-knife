---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MainMenu`](#️-class-mainmenu)
  - [⚙️ Method `__init__`](#️-method-__init__)
- [🔧 Function `main`](#-function-main)

</details>

## 🏛️ Class `MainMenu`

```python
class MainMenu(hsk.main_menu_base.MainMenuBase)
```

Main menu class that defines the application's menu structure.

This class extends the MainMenuBase class and creates all the menu items
and submenus for the application.

<details>
<summary>Code:</summary>

```python
class MainMenu(hsk.main_menu_base.MainMenuBase):

    def __init__(self, *, output_bus: ActionOutputBus) -> None:
        """Initialize the main menu with all submenus and actions.

        Create and organizes all menu categories and their respective items.
        """
        super().__init__(output_bus=output_bus)
        self.add_menu_structure(self.menu, get_menu_structure())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Initialize the main menu with all submenus and actions.

Create and organizes all menu categories and their respective items.

<details>
<summary>Code:</summary>

```python
def __init__(self, *, output_bus: ActionOutputBus) -> None:
        super().__init__(output_bus=output_bus)
        self.add_menu_structure(self.menu, get_menu_structure())
```

</details>

## 🔧 Function `main`

```python
def main() -> None
```

Run the Harrix Swiss Knife application (tray icon and optional main window).

<details>
<summary>Code:</summary>

```python
def main() -> None:
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
        tb = traceback.format_exc()
        log.exception("Fatal error during startup; exiting.")
        show_fatal_error_dialog(f"Fatal error during startup.\n\nLog: {log_path}\n\n{tb}")
        sys.exit(1)
```

</details>
