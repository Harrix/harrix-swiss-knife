---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tray_icon.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TrayIcon`](#%EF%B8%8F-class-trayicon)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `active (classmethod)`](#%EF%B8%8F-method-active-classmethod)
  - [⚙️ Method `ensure_main_window`](#%EF%B8%8F-method-ensure_main_window)
  - [⚙️ Method `on_activated`](#%EF%B8%8F-method-on_activated)
  - [⚙️ Method `show_command_window`](#%EF%B8%8F-method-show_command_window)
- [🔧 Function `show_command_window`](#-function-show_command_window)

</details>

## 🏛️ Class `TrayIcon`

```python
class TrayIcon(QSystemTrayIcon)
```

Represent a system tray icon with an associated context menu and main window.

Attributes:

- `main_window` (`main_window.MainWindow | None`):
  The main window associated with the tray icon. Defaults to `None`.
- `menu` (`QMenu`):
  The context menu displayed when interacting with the tray icon.

<details>
<summary>Code:</summary>

```python
class TrayIcon(QSystemTrayIcon):

    _instance: ClassVar[TrayIcon | None] = None

    def __init__(
        self,
        icon: QIcon,
        menu: QMenu,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the `TrayIcon` with the given icon and menu.

        Args:

        - `icon` (`QIcon`):
          The icon to display in the system tray.
        - `menu` (`QMenu`):
          The context menu to associate with the tray icon.
        - `parent` (`QWidget | None`):
          The parent widget. Defaults to `None`.

        Sets up the system tray icon, context menu, and connects the activation signal
        to handle user interactions.

        """
        super().__init__(icon, parent)
        TrayIcon._instance = self
        set_menu_tooltips_visible_recursive(menu)
        self.setContextMenu(menu)
        self.activated.connect(self.on_activated)
        self.main_window: main_window.MainWindow | None = None
        self.menu: QMenu = menu

    @classmethod
    def active(cls) -> TrayIcon | None:
        """Return the process tray icon, if one was created."""
        return cls._instance

    def ensure_main_window(self) -> main_window.MainWindow:
        """Create the main window on first use."""
        if self.main_window is None:
            self.main_window = main_window.MainWindow(self.menu)
        return self.main_window

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle the activation event of the system tray icon.

        Args:

        - `reason` (`QSystemTrayIcon.ActivationReason`):
          The reason for the activation event.

        If the tray icon is clicked (Trigger), it shows and brings the main window to the front.

        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_command_window()

    def show_command_window(self) -> None:
        """Show the command-cards window and bring it to the front."""
        window = self.ensure_main_window()
        window.show()
        window.raise_()
        window.activateWindow()
        window.focus_initial_input()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, icon: QIcon, menu: QMenu, parent: QWidget | None = None) -> None
```

Initialize the [`TrayIcon`](#%EF%B8%8F-class-trayicon) with the given icon and menu.

Args:

- `icon` (`QIcon`):
  The icon to display in the system tray.
- `menu` (`QMenu`):
  The context menu to associate with the tray icon.
- `parent` (`QWidget | None`):
  The parent widget. Defaults to `None`.

Sets up the system tray icon, context menu, and connects the activation signal
to handle user interactions.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        icon: QIcon,
        menu: QMenu,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(icon, parent)
        TrayIcon._instance = self
        set_menu_tooltips_visible_recursive(menu)
        self.setContextMenu(menu)
        self.activated.connect(self.on_activated)
        self.main_window: main_window.MainWindow | None = None
        self.menu: QMenu = menu
```

</details>

### ⚙️ Method `active (classmethod)`

```python
def active(cls) -> TrayIcon | None
```

Return the process tray icon, if one was created.

<details>
<summary>Code:</summary>

```python
def active(cls) -> TrayIcon | None:
        return cls._instance
```

</details>

### ⚙️ Method `ensure_main_window`

```python
def ensure_main_window(self) -> main_window.MainWindow
```

Create the main window on first use.

<details>
<summary>Code:</summary>

```python
def ensure_main_window(self) -> main_window.MainWindow:
        if self.main_window is None:
            self.main_window = main_window.MainWindow(self.menu)
        return self.main_window
```

</details>

### ⚙️ Method `on_activated`

```python
def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None
```

Handle the activation event of the system tray icon.

Args:

- `reason` (`QSystemTrayIcon.ActivationReason`):
  The reason for the activation event.

If the tray icon is clicked (Trigger), it shows and brings the main window to the front.

<details>
<summary>Code:</summary>

```python
def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_command_window()
```

</details>

### ⚙️ Method `show_command_window`

```python
def show_command_window(self) -> None
```

Show the command-cards window and bring it to the front.

<details>
<summary>Code:</summary>

```python
def show_command_window(self) -> None:
        window = self.ensure_main_window()
        window.show()
        window.raise_()
        window.activateWindow()
        window.focus_initial_input()
```

</details>

## 🔧 Function `show_command_window`

```python
def show_command_window() -> bool
```

Show the tray command-cards window when a tray icon exists.

Returns:

- `bool`: `True` when the window was shown.

<details>
<summary>Code:</summary>

```python
def show_command_window() -> bool:
    tray = TrayIcon.active()
    if tray is None:
        return False
    tray.show_command_window()
    return True
```

</details>
